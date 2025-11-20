{ pkgs, inputs }:
pkgs.mkShell {
  # Add build dependencies
  packages = [
    inputs.backlog.packages.${pkgs.system}.default
    pkgs.socat
    pkgs.bubblewrap
  ];

  # Add environment variables
  env = { };

  # Load custom bash code
  shellHook = ''

  '';
}
