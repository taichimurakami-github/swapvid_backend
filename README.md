# SwapVid Backend Components (Sequence Analyzer, etc)

Source Code of "SwapVid: Integrating Video Viewing and Document Exploration (CHI2024 Paper)."

- DOI: **10.1145/3613904.3642515**

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

**[Docker Desktop](https://www.docker.com/ja-jp/products/docker-desktop/) is required.**

### Running services

Please run the following command to build the container.

```bash
docker compose up
```

It can take ~20 minitues.

After the build is finished, Sequence Analyzer and other services are avairable from localhost.

All services and required ports are written in `./src/config.yml`.

**Please ensure that all ports are available in your computer**. (For example, Sequence Analyzer can available at **http://localhost:8881**.)

Also, you can access the services from the other devices(i.e. iPad) connected to the same network. Please check your PC's ip address.

### Removing the container

Please run the following command:

```bash
docker compose down --rmi "all" --remove-orphans -v
```

## Authors

- **Taichi Murakami** - Tohoku University, Japan
- **Kazuyuki Fujita** - Tohoku University, Japan
- **Kotaro Hara** - Singapore Management University, Singapore
- **Kazuki Takashima** - Tohoku University, Japan
- **Yoshifumi Kitamura** - Tohoku University, Japan

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This work is licensed under [a Creative Commons Attribution International 4.0 License](https://creativecommons.org/licenses/by/4.0/).
