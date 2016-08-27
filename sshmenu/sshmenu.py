import argparse
import json
import os
import readchar
import sys
import time

from subprocess import call, Popen, PIPE
from clint import resources
from clint.textui import puts, colored


def main():
    # Check arguments
    parser = argparse.ArgumentParser(prog='sshmenu', description='A convenient tool for bookmarking hosts and connecting to them via ssh.')
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
        puts('I have created a new configuration file, please edit and run again:')
        puts(resources.user.path + os.path.sep + config_name)
    else:
        config = json.loads(resources.user.read(config_name))
        display_menu(config['targets'])

def get_terminal_height():
    # Return height of terminal as int
    tput = Popen(["tput", "lines"], stdout=PIPE)
    height, stderr = tput.communicate()

    return(int(height))

def display_menu(targets):
    # We need at least one target for our UI to make sense
    num_targets = len(targets)
    if num_targets <= 0:
        puts('Whoops, you don\'t have any targets listed in your config!')
        exit(0)

    # Determine the longest host and line length
    longest_host = -1
    longest_line = -1
    for index, target in enumerate(targets):
        length = len(target['host'])
        # Check host length
        if length > longest_host:
            longest_host = length

        # Generate description and check line length
        desc = '%2d ' % (index) + target['host'].ljust(longest_host) + ' | ' + target['friendly']
        target['desc'] = desc
        line_length = len(desc)
        if line_length > longest_line:
            longest_line = line_length

    # Clear screen
    call(['tput', 'clear'])

    # Save current cursor position so we can overwrite on list updates
    call(['tput', 'sc'])

    # Keep track of currently selected target
    selected_target = 0

    # Support input of long numbers
    number_buffer = []
    # Store time of last number that was entered
    number_last = round(time.time())
    # Get initial terminal height
    terminal_height = get_terminal_height()
    # Set initial visible target range. Subtract 2 because one line is used by the instructions, and one line is always empty at the bottom.
    visible_target_range = range(terminal_height - 2)

    while True:
        # Calculate height of terminal window in case it has been resized
        new_terminal_height = get_terminal_height()
        # Return to the saved cursor position
        call(['tput', 'rc'])

        # Redraw the instructions to make sure they don't disappear when resizing terminal
        puts(colored.cyan('Select a target (up (k), down (j), enter, ctrl+c to exit)'))

        # Recalculate visible targets based on selected_target
        move_down = False
        move_up = False
        if terminal_height != new_terminal_height:
            if selected_target + (terminal_height - 2) > num_targets:
                move_down = True
            else:
                move_up = True

            terminal_height = new_terminal_height

        if selected_target > max(visible_target_range) or move_down:
            visible_start = selected_target - terminal_height + 3
            visible_end = selected_target + 1
            visible_target_range = range(visible_start, visible_end)

        elif selected_target < min(visible_target_range) or move_up:
            visible_start = selected_target
            visible_end = selected_target + terminal_height - 2
            visible_target_range = range(visible_start, visible_end)

        # Print items
        for index, target in enumerate(targets):
            # Only print the items that are within the visible range.
            # Due to lines changing their position on the screen when scrolling,
            # we need to redraw the entire line + add padding to make sure all 
            # traces of the previous line are erased.
            if index in visible_target_range:
                if index == selected_target:
                    puts(colored.green(' -> ' + target['desc'].ljust(longest_line)))
                else:
                    puts('    ' + target['desc'].ljust(longest_line))

        # Hang until we get a keypress
        key = readchar.readkey()

        if key == readchar.key.UP or key == 'k':
            # Ensure the new selection would be valid
            if (selected_target - 1) >= 0:
                selected_target -= 1

            # Empty the number buffer
            number_buffer = []

        elif key == readchar.key.DOWN or key == 'j':
            # Ensure the new selection would be valid
            if (selected_target + 1) <= (num_targets - 1):
                selected_target += 1

            # Empty the number buffer
            number_buffer = []

        elif key == 'g':
            # Go to top
            selected_target = 0

            # Empty the number buffer
            number_buffer = []

        elif key == 'G':
            # Go to bottom
            selected_target = num_targets - 1

            # Empty the number buffer
            number_buffer = []

        # Check if key is a number
        elif key in map(lambda x: str(x), range(10)):
            requested_target = int(key)

            # Check if there are any previously entered numbers, and append if less than one second has gone by
            if round(time.time()) - number_last <= 1:
                number_buffer += key
                requested_target = int(''.join(number_buffer))
                # If the new target is invalid, just keep the previously selected target instead
                if requested_target >= num_targets:
                    requested_target = selected_target
            else:
                number_buffer = [key]

            number_last = round(time.time())

            # Ensure the new selection would be valid
            if requested_target >= num_targets:
                requested_target = num_targets - 1

            selected_target = requested_target

        elif key == readchar.key.ENTER:
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
                sys.exit('command not found: {commandname}'.format(commandname=command))

        elif key == readchar.key.CTRL_C:
            exit(0)
