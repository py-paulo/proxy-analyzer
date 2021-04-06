# Analyzer

__**Analyzer**__ é um conjunto de ferramentas que faz o monitoramento, armazenamento e análise do tráfego *web* que passa pelo [proxy](https://github.com/py-paulo/proxy.py) para múltiplos propósitos, mas inicialmente pensado com foco em segurança, rastreando conexões suspeitas com hosts inseguros, trazendo métricas e informações valiosas para identificar comportamento de malwares em geral.

## Instalação

> Para rodar o projeto você precisa [Docker](https://www.docker.com/get-started) e [docker-compose](https://docs.docker.com/compose/).

Basta fazer o clone do projeto:
```
git clone https://github.com/py-paulo/analyzer.git
```
Em seguida executar o script ``ini.sh``, caso sua plataforma seja *Windows* basta fazer o clone do projeto [proxy.py](https://github.com/py-paulo/proxy.py.git).
```
git clone https://github.com/py-paulo/proxy.py.git
```

O **Analyzer** sobe os seguintes serviços:
* **proxy** [8899]
    > Este projeto é um fork do [proxy.py](https://github.com/abhinavsingh/proxy.py) por ``abhinavsin`` com a alteração de um novo plugin para enviar todos os logs para a aplicação web ``kafka-proxy``.
* **kafka-proxy** [8000]
    > Como descrito acima, é uma aplicação web (*REST Api*) escrita em *Socket* para otimizar e garantir a eficiencia no envio dos logs para o *Kafka*.
* **zookeeper** [2181]
* **kafka** [9092]

![Arch](img/analyzer-arch.png?raw=true "Arch")