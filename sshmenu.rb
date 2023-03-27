class Sshmenu < Formula
  include Language::Python::Virtualenv

  homepage "https://github.com/mmeyer724/sshmenu"
  url "https://github.com/mmeyer724/sshmenu/archive/0.0.5.tar.gz"
  sha256 "f7c5c4e36c6e2e553fb3130a8c08761fb03628ac17d0f683a93bb2959fb2648f"

  depends_on "python3"

  resource "args" do
    url "https://files.pythonhosted.org/packages/e5/1c/b701b3f4bd8d3667df8342f311b3efaeab86078a840fb826bd204118cc6b/args-0.1.0.tar.gz"
    sha256 "a785b8d837625e9b61c39108532d95b85274acd679693b71ebb5156848fcf814"
  end

  resource "clint" do
    url "https://files.pythonhosted.org/packages/3d/b4/41ecb1516f1ba728f39ee7062b9dac1352d39823f513bb6f9e8aeb86e26d/clint-0.5.1.tar.gz"
    sha256 "05224c32b1075563d0b16d0015faaf9da43aa214e4a2140e51f08789e7a4c5aa"
  end

  resource "readchar" do
    url "https://files.pythonhosted.org/packages/61/a9/d552ab5bb2978b609a0acc917427fb0230ac923d92e32b817ef79908f6e3/readchar-0.7.tar.gz"
    sha256 "c3354162894634ff6a29a06a1cd04c92522f32b7bc6c17e247cf3bee27ee914c"
  end

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    false
  end
end