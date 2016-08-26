class Sshmenu < Formula
  homepage "https://github.com/Mike724/sshmenu"
  url "https://pypi.python.org/packages/91/f6/ea336cb25529c87309899abc1fab2a669f1334c3ac77ee8e279de3855102/sshmenu-0.0.3.tar.gz"
  sha256 "8078a55f0a6965763c8bf2cbba1fe7016d68ab142db5c1a09abe8369ef288ae7"

  depends_on :python3

  resource "args" do
    url "https://pypi.python.org/packages/e5/1c/b701b3f4bd8d3667df8342f311b3efaeab86078a840fb826bd204118cc6b/args-0.1.0.tar.gz"
    sha256 "a785b8d837625e9b61c39108532d95b85274acd679693b71ebb5156848fcf814"
  end

  resource "clint" do
    url "https://pypi.python.org/packages/3d/b4/41ecb1516f1ba728f39ee7062b9dac1352d39823f513bb6f9e8aeb86e26d/clint-0.5.1.tar.gz"
    sha256 "05224c32b1075563d0b16d0015faaf9da43aa214e4a2140e51f08789e7a4c5aa"
  end

  resource "readchar" do
    url "https://pypi.python.org/packages/61/a9/d552ab5bb2978b609a0acc917427fb0230ac923d92e32b817ef79908f6e3/readchar-0.7.tar.gz"
    sha256 "c3354162894634ff6a29a06a1cd04c92522f32b7bc6c17e247cf3bee27ee914c"
  end

  def install
    xy = Language::Python.major_minor_version "python3"
    ENV.prepend_create_path "PYTHONPATH", libexec/"vendor/lib/python#{xy}/site-packages"
    %w[args clint readchar].each do |r|
      resource(r).stage do
        system "python3", *Language::Python.setup_install_args(libexec/"vendor")
      end
    end

    ENV.prepend_create_path "PYTHONPATH", libexec/"lib/python#{xy}/site-packages"
    system "python3", *Language::Python.setup_install_args(libexec)

    bin.install Dir[libexec/"bin/*"]
    bin.env_script_all_files(libexec/"bin", :PYTHONPATH => ENV["PYTHONPATH"])
  end
end
