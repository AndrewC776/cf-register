#BRG365 

This project is to solve the problem of [BRG365](https://brg365.com) automatic deployment of domain name resolution. It can batch configure goodaddy domain names, resolve cloudflare services according to configuration rules, customize and optimize cache and WAF rule configuration.


main.py is the main program script, which implements 2 functions:
1. When running for the first time, it will automatically download the domain name configuration information of cloudflare online to the local computer, and the default is the online_dns_records.yaml file (overwrite mode, if it already exists locally, it will overwrite the local computer)
2. Manually modify the file: copy the generated content online_dns_records.yaml->paste it into dns_records.yaml, and modify it to the settings you need
3. After the program starts, detect the existence of dns_records.yaml and update the online configuration

change_godady_ns_to_cf.py implements the configuration of specifying the godaddy domain name to point to a specific nameserver service address (be sure to modify nameservers, api_key, api_secret before use)

The links that have been tested are as follows domain:

[https://www.patreon.com/posts/estatisticas-de-121265072](https://www.patreon.com/posts/estatisticas-de-121265072)  
[https://wakelet.com/wake/ZtzpuNQw9ESzCk8JLdyG1](https://wakelet.com/wake/ZtzpuNQw9ESzCk8JLdyG1)