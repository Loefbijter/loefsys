{
  description = "Development environment for loefsys";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          python = pkgs.python314;
        in
        {
          default = pkgs.mkShell {
            packages = [
              python
              pkgs.uv
              pkgs.tailwindcss_4
              # msgfmt/xgettext for compilemessages and makemessages.
              pkgs.gettext
            ];

            env = {
              # uv manages .venv with the dependencies from uv.lock, on Nix's Python.
              UV_PYTHON = python.interpreter;
              UV_PYTHON_DOWNLOADS = "never";
              TAILWIND_BIN_PATH = "${pkgs.tailwindcss_4}/bin/tailwindcss";
              # Browsers for the e2e tests; keep `playwright` in pyproject.toml on the
              # same version as nixpkgs' playwright-driver.
              PLAYWRIGHT_BROWSERS_PATH = "${pkgs.playwright-driver.browsers}";
              PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = "true";
              # Binary wheels in .venv (e.g. greenlet) link against libstdc++.
              LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ];
            };

            shellHook = ''
              unset PYTHONPATH
              uv sync --all-groups --quiet
              source .venv/bin/activate
            '';
          };
        }
      );
    };
}
