{
  description = "DPD Experimentation";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
    naersk.url = "github:nix-community/naersk/pull/391/head";
  };

  outputs = inputs@{ flake-parts, ... }:
  flake-parts.lib.mkFlake { inherit inputs; } ({ ... }: {
    systems = import inputs.systems;

    perSystem = { pkgs, self', ... }: let
      naerskLib = pkgs.callPackage inputs.naersk {};
      row = naerskLib.buildPackage {
        src = pkgs.fetchFromGitHub {
          owner = "glotzerlab";
          repo = "row";
          rev = "trunk"; # glotzerlab uses trunk as their default branch
          hash = "sha256-zw1TNusZBhoqEbuSEBVMOnLP4YE1W6XP4Iue7Cy3cCw=";
        };
        buildInputs = [ pkgs.openssl ];
        nativeBuildInputs = [ pkgs.pkg-config ];
      };
    in {
      packages.row = row;

      devShells.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          conda
          row
        ];
      };
    };
  });
}
