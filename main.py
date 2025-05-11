from modules.network_scanner import NetworkScanner
from exploit_modules.ssh_exploiter import SSHExploiter
from exploit_modules.http_exploiter import HTTPExploiter
import json

def main():
    print("Iniciando programa de Pentest Automatizado...")
    
    target = "localhost" # Para testes locais
    # target = "scanme.nmap.org" # Alvo público para testes. Cuidado com escaneamentos agressivos.
    
    print(f"Criando instância do NetworkScanner para o alvo: {target}")
    scanner = NetworkScanner()
    
    print(f"\n--- Realizando varredura padrão em {target} ---")
    ports_to_scan = "21,22,23,25,53,80,110,135,139,443,445,1433,1521,3306,3389,5432,5900,8080"
    if target == "scanme.nmap.org":
        ports_to_scan = "22,80,443,9929,31337" # Portas conhecidas do scanme
        
    results = scanner.scan_host(target, ports=ports_to_scan)
    
    if results:
        print(f"\nResultados da varredura em {target}:")
        print(json.dumps(results, indent=4))
        
        for host_ip, host_data in results.items():
            if host_data.get('state') == 'up':
                print(f"\nAnalisando portas abertas e iniciando módulos de exploração para {host_ip}...")
                if 'tcp' in host_data.get('protocols', {}):
                    for port, port_data in host_data['protocols']['tcp'].items():
                        if port_data.get('state') == 'open':
                            service_name = port_data.get('name', 'N/A')
                            print(f"  Porta TCP {port} ({service_name}) está aberta.")
                            
                            # Lógica para acionar módulos de exploração
                            if port == 22 or service_name == 'ssh':
                                print(f"    -> Serviço SSH detectado na porta {port}. Acionando SSHExploiter...")
                                ssh_module = SSHExploiter(target_host=host_ip, port=port)
                                ssh_module.attempt_bruteforce(['admin', 'root'], ['password', '12345']) # Simulação
                                ssh_module.check_known_vulnerabilities() # Simulação
                            
                            elif port == 80 or service_name == 'http':
                                print(f"    -> Serviço HTTP detectado na porta {port}. Acionando HTTPExploiter...")
                                http_module = HTTPExploiter(target_host=host_ip, port=port, protocol='http')
                                http_module.check_common_vulnerabilities() # Simulação

                            elif port == 443 or service_name == 'https':
                                print(f"    -> Serviço HTTPS detectado na porta {port}. Acionando HTTPExploiter...")
                                https_module = HTTPExploiter(target_host=host_ip, port=port, protocol='https')
                                https_module.check_common_vulnerabilities() # Simulação
                            
                            # Adicionar mais condições para outros serviços e módulos aqui
                            # Ex: FTP, SMTP, SMB, SQL Databases etc.
                            
    else:
        print(f"Nenhum resultado obtido para {target} ou o host está inativo.")

    print("\nPrograma de Pentest Automatizado (fase de exploração dinâmica) concluído por enquanto.")

if __name__ == "__main__":
    main()

