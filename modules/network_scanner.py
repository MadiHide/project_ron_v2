import nmap
import json

class NetworkScanner:
    def __init__(self):
        self.nm = nmap.PortScanner()

    def scan_host(self, target_host, ports='22,80,443', arguments='-sV -T4'):
        """
        Realiza uma varredura no host especificado.

        :param target_host: O host a ser varrido (IP ou nome de domínio).
        :param ports: As portas a serem varridas (ex: '22,80,443').
        :param arguments: Argumentos do Nmap (ex: '-sV -T4').
        :return: Um dicionário com os resultados da varredura ou None se o host estiver inativo ou houver erro.
        """
        print(f"Iniciando varredura em {target_host} nas portas {ports} com argumentos {arguments}")
        try:
            self.nm.scan(hosts=target_host, ports=ports, arguments=arguments)
            scan_results = {}
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    scan_results[host] = {
                        'hostname': self.nm[host].hostname(),
                        'state': self.nm[host].state(),
                        'protocols': {}
                    }
                    for proto in self.nm[host].all_protocols():
                        scan_results[host]['protocols'][proto] = {}
                        lport = self.nm[host][proto].keys()
                        for port in lport:
                            scan_results[host]['protocols'][proto][port] = self.nm[host][proto][port]
                else:
                    print(f"Host {host} está {self.nm[host].state()}")
                    return None # Retorna None se o host não estiver 'up'
            
            if not scan_results:
                print(f"Nenhum host ativo encontrado ou nenhuma informação coletada para {target_host}")
                return None

            return scan_results
        except nmap.PortScannerError as e:
            print(f"Erro do Nmap: {e}")
            return None
        except Exception as e:
            print(f"Ocorreu um erro inesperado durante a varredura: {e}")
            return None

if __name__ == '__main__':
    # Exemplo de uso
    scanner = NetworkScanner()
    target = 'scanme.nmap.org' # Alvo para teste, público e seguro
    #target = '127.0.0.1' # Para testes locais
    print(f"Testando NetworkScanner com o alvo: {target}")
    
    # Teste 1: Varredura padrão (portas comuns, detecção de serviço)
    results = scanner.scan_host(target)
    if results:
        print("Resultados da Varredura Padrão:")
        print(json.dumps(results, indent=4))
    else:
        print(f"Varredura padrão em {target} não retornou resultados ou o host está inativo.")

    print(f"\n{'-'*50}\n")

    # Teste 2: Varredura em porta específica (ex: porta 22 - SSH)
    results_ssh = scanner.scan_host(target, ports='22', arguments='-sV')
    if results_ssh:
        print("Resultados da Varredura na Porta 22 (SSH):")
        print(json.dumps(results_ssh, indent=4))
    else:
        print(f"Varredura na porta 22 em {target} não retornou resultados ou o host está inativo.")

    print(f"\n{'-'*50}\n")

    # Teste 3: Varredura com argumentos para detecção de OS (requer sudo/root)
    # Nota: A detecção de OS (-O) geralmente requer privilégios de root.
    # Se não estiver rodando como root, este scan pode falhar ou não detectar o OS.
    # results_os = scanner.scan_host(target, arguments='-O')
    # if results_os:
    #     print("Resultados da Varredura com Detecção de OS:")
    #     print(json.dumps(results_os, indent=4))
    # else:
    #     print(f"Varredura com detecção de OS em {target} não retornou resultados ou o host está inativo.")

    print("Testes do NetworkScanner concluídos.")

