# Load Balancer

## What is a Load Balancer?
A load balancer is a device or software application that distributes network or application traffic across multiple servers. Load balancers are used to improve the reliability and scalability of applications by evenly distributing incoming requests.

## Installation
To get started with the Load Balancer project, follow these steps:

1. Clone the repository:
    ```bash
    git clone <repository_url>
    ```
2. Navigate to the project directory:
    ```bash
    cd <directory>
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To initiate the Load Balancer and keep it running, execute the following command:
```bash
python lb.py
```


## Parameters

The Load Balancer accepts the following parameters:

- `--backend-servers`: Specifies the backend servers to distribute traffic to. You can pass multiple servers separated by spaces. Default value is `['127.0.0.1:8080', '127.0.0.1:8081', '127.0.0.1:8082']`.
- `--health-check-interval`: Specifies the interval (in seconds) for health checks on backend servers. Default value is `5`.

## Load Testing
To do load testing, run the urls.txt file using curl command.
```bash
curl --parallel --parallel-immediate --parallel-max 3 --config urls.txt
```

This should initiate all requests concurrently and you should be able to see requests distributed among different servers.