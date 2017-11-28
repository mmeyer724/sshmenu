import argparse
import json
import os
import readchar
import sys
import time
import readline

from subprocess import call, Popen, PIPE
from clint import resources
from clint.textui import puts, colored

targets = []
config_name = ''

# Time to sleep between transitions
TRANSITION_DELAY_TIME = 0.5

NUMBER_ENTRY_EXPIRE_TIME = 0.75


def main():
    global config_name

    # Check arguments
    parser = argparse.ArgumentParser(prog='sshmenu',
                                     description='A convenient tool for bookmarking '
                                                 'hosts and connecting to them via ssh.')
    parser.add_argument('-c', '--configname', default='config', help='Specify an alternate configuration name.')
    args = parser.parse_args()

    # Get config name
    config_name = '{configname}.json'.format(configname=args.configname)

    # First parameter is 'company' name, hence duplicate arguments
    resources.init('sshmenu', 'sshmenu')

    # If the config file doesn't exist, create an example config
    if resources.user.read(config_name) is None:
        example_config = {
            'targets': [
                {
                    'host': 'user@example-machine.local',
                    'friendly': 'This is an example target',
                    'options': []
                },
                {
                    'command': 'mosh',
                    'host': 'user@example-machine.local',
                    'friendly': 'This is an example target using mosh',
                    'options': []
                }
            ]
        }
        resources.user.write(config_name, json.dumps(example_config, indent=4))

    update_targets()
    display_menu()


def get_terminal_height():
    # Return height of terminal as int
    tput = Popen(['tput', 'lines'], stdout=PIPE)
    height, stderr = tput.communicate()

    return int(height)


def display_help():
    # Clear screen and show the help text
    call(['clear'])
    puts(colored.cyan('Available commands (press any key to exit)'))

    puts(' enter       - Connect to your selection')
    puts(' crtl+c | q  - Quit sshmenu')
    puts(' k (up)      - Move your selection up')
    puts(' j (down)    - Move your selection down')
    puts(' h           - Show help menu')
    puts(' c           - Create new connection')
    puts(' d           - Delete connection')
    puts(' e           - Edit connection')
    puts(' + (plus)    - Move connection up')
    puts(' - (minus)   - Move connection down')

    # Hang until we get a keypress
    readchar.readkey()


def connection_create():
    global config_name

    call(['clear'])
    puts(colored.cyan('Create new connection entry'))
    puts('')

    host = input('Hostname (user@machine): ')

    if host is '':
        puts('')
        puts('Nothing done')
        time.sleep(TRANSITION_DELAY_TIME)
        return

    friendly = input('Description []: ')
    command = input('Command [ssh]: ')
    options = input('Command Options []: ')

    # Set the defaults if our input was empty
    command = 'ssh' if command == '' else command
    options = [] if options == '' else options.split()

    # Append the new target to the config
    config = json.loads(resources.user.read(config_name))
    config['targets'].append({'command': command, 'host': host, 'friendly': friendly, 'options': options})

    # Save the new config
    resources.user.write(config_name, json.dumps(config, indent=4))
    update_targets()

    puts('')
    puts('New connection added')
    time.sleep(TRANSITION_DELAY_TIME)


def connection_edit(selected_target):
    global targets, config_name

    call(['clear'])
    puts(colored.cyan('Editing connection %s' % targets[selected_target]['host']))
    puts('')

    target = targets[selected_target]

    while True:
        host = input_prefill('Hostname: ', target['host'])
        if host is not '':
            break

    friendly = input_prefill('Description: ', target['friendly'])
    command = input_prefill('Command [ssh]: ', 'ssh' if not target.get('command') else target['command'])
    options = input_prefill('Options []: ', ' '.join(target['options']))

    # Set the defaults if our input was empty
    command = 'ssh' if command == '' else command
    options = [] if options == '' else options.split()

    # Delete the old entry insert the edited one in its place
    config = json.loads(resources.user.read(config_name))
    del config['targets'][selected_target]
    config['targets'].insert(selected_target,
                             {'command': command, 'host': host, 'friendly': friendly, 'options': options})

    resources.user.write(config_name, json.dumps(config, indent=4))
    update_targets()

    puts('')
    puts('Changes saved')
    time.sleep(TRANSITION_DELAY_TIME)


def connection_delete(selected_target):
    global targets, config_name

    call(['clear'])
    puts(colored.red('Delete connection entry for %s' % targets[selected_target]['host']))
    puts('')

    while True:
        response = input('Are you sure you want to delete this connection [yes|NO]: ').lower()

        if response == 'no' or response == 'n' or response == '':
            puts('')
            puts('Nothing done')
            break

        if response == 'yes':
            config = json.loads(resources.user.read(config_name))
            del config['targets'][selected_target]

            resources.user.write(config_name, json.dumps(config, indent=4))
            update_targets()

            puts('')
            puts('Connection deleted')
            break

    time.sleep(TRANSITION_DELAY_TIME)


def connection_move_up(selected_target):
    global config_name

    config = json.loads(resources.user.read(config_name))
    config['targets'].insert(selected_target - 1, config['targets'].pop(selected_target))

    resources.user.write(config_name, json.dumps(config, indent=4))
    update_targets()


def connection_move_down(selected_target):
    global config_name

    config = json.loads(resources.user.read(config_name))
    config['targets'].insert(selected_target + 1, config['targets'].pop(selected_target))

    resources.user.write(config_name, json.dumps(config, indent=4))
    update_targets()


def update_targets():
    global targets, config_name

    config = json.loads(resources.user.read(config_name))
    if 'targets' in config:
        targets = config['targets']


def display_menu():
    global targets

    # Save current cursor position so we can overwrite on list updates
    call(['tput', 'clear', 'sc'])

    # Keep track of currently selected target
    selected_target = 0

    # Support input of long numbers
    number_buffer = []

    # Store time of last number that was entered
    time_last_digit_pressed = round(time.time())

    # Get initial terminal height
    terminal_height = get_terminal_height()

    # Set initial visible target range.
    # Subtract 2 because one line is used by the instructions,
    # and one line is always empty at the bottom.
    visible_target_range = range(terminal_height - 2)

    while True:
        # Return to the saved cursor position
        call(['tput', 'clear', 'rc'])

        # We need at least one target for our UI to make sense
        num_targets = len(targets)
        if num_targets <= 0:
            puts(colored.red('Whoops, you don\'t have any connections defined in your config!'))
            puts('')
            puts('Press "c" to create a new connection')
        else:
            puts(colored.cyan('Select a target (press "h" for help)'))

            # Determine the longest host
            longest_host = -1
            longest_line = -1
            for index, target in enumerate(targets):
                length = len(target['host'])
                # Check host length
                if length > longest_host:
                    longest_host = length

            # Generate description and check line length
            for index, target in enumerate(targets):
                desc = target['host'].ljust(longest_host) + ' | ' + target['friendly']
                target['desc'] = desc
                line_length = len(desc)
                if line_length > longest_line:
                    longest_line = line_length

            # Recalculate visible targets based on selected_target
            if selected_target > max(visible_target_range):
                visible_start = selected_target - terminal_height + 3
                visible_end = selected_target + 1
                visible_target_range = range(visible_start, visible_end)
            elif selected_target < min(visible_target_range):
                visible_start = selected_target
                visible_end = selected_target + terminal_height - 2
                visible_target_range = range(visible_start, visible_end)

            # Make sure our selected target is not higher than possible
            # This can happen if you delete the last target
            selected_target = selected_target if selected_target < num_targets else 0

            # Used to pad out the line numbers so that we can keep everything aligned
            num_digits = len(str(num_targets))
            digits_format_specifier = '%' + str(num_digits) + 'd'

            # Print items
            for index, target in enumerate(targets):
                # Only print the items that are within the visible range.
                # Due to lines changing their position on the screen when scrolling,
                # we need to redraw the entire line + add padding to make sure all
                # traces of the previous line are erased.
                if index in visible_target_range:
                    line = (digits_format_specifier + '. %s ') % (index + 1, target['desc'].ljust(longest_line))
                    if index == selected_target:
                        puts(colored.green(' -> %s' % line))
                    else:
                        puts(colored.white('    %s' % line))

        # Hang until we get a keypress
        key = readchar.readkey()

        if key == readchar.key.UP or key == 'k' and num_targets > 0:
            # Ensure the new selection would be valid & reset number input buffer
            if (selected_target - 1) >= 0:
                selected_target -= 1
            number_buffer = []

        elif key == readchar.key.DOWN or key == 'j' and num_targets > 0:
            # Ensure the new selection would be valid & reset number input buffer
            if (selected_target + 1) <= (num_targets - 1):
                selected_target += 1
            number_buffer = []

        elif key == 'g':
            # Go to top & reset number input buffer
            selected_target = 0
            number_buffer = []

        elif key == 'G':
            # Go to bottom & reset number input buffer
            selected_target = num_targets - 1
            number_buffer = []

        # Check if key is a number
        elif key in map(lambda x: str(x), range(10)):
            current_time = time.time()
            if current_time - time_last_digit_pressed >= NUMBER_ENTRY_EXPIRE_TIME:
                number_buffer = []
            time_last_digit_pressed = current_time

            number_buffer += key
            new_selection = int(''.join(number_buffer))

            # If the new target is invalid, just keep the previously selected target instead
            if num_targets >= new_selection > 0:
                selected_target = new_selection - 1

        elif key == readchar.key.ENTER and num_targets > 0:
            # For cleanliness clear the screen
            call(['tput', 'clear'])

            target = targets[selected_target]

            # Check if there is a custom command for this target
            if 'command' in target.keys():
                command = target['command']
            else:
                command = 'ssh'

            # Arguments to the child process should start with the name of the command being run
            args = [command] + target.get('options', []) + [target['host']]
            try:
                # After this line, ssh will replace the python process
                os.execvp(command, args)
            except FileNotFoundError:
                sys.exit('Command not found: {commandname}'.format(commandname=command))

        elif key == 'h':
            display_help()

        elif key == 'c':
            connection_create()

        elif key == 'd' and num_targets > 0:
            connection_delete(selected_target)

        elif key == 'e' and num_targets > 0:
            connection_edit(selected_target)

        elif key == '-' and num_targets > 0:
            if selected_target < num_targets:
                connection_move_down(selected_target)
                selected_target += 1

        elif key == '+' and num_targets > 0:
            if selected_target > 0:
                connection_move_up(selected_target)
                selected_target -= 1

        elif key == readchar.key.CTRL_C or key == 'q':
            exit(0)


def input_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()

    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result
