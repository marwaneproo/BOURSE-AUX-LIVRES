{
  description = "pfa django dev environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: let
    system = "x86_64-linux";

    pkgs = import nixpkgs {inherit system;};

    pythonEnv = pkgs.python312.withPackages (ps:
      with ps; [
        django
        django-stubs
        pillow
        python-decouple
        djangorestframework
        djangorestframework-simplejwt
        django-cors-headers
        daphne
        channels
        channels-redis
      ]);
  in {
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        pythonEnv
        /*
           pkgs.tesseract
        pkgs.zbar
        */
      ];
    };
  };
}
