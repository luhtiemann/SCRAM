import socket
import MyHashLib as HL
# O servidor ALICE foi comprometido através de um ataque do tipo Watering Hole
# CHARLES induziu a ALICE a instalar um programa com malware que intercepta os 
pacotes enviados para rede e envia uma cópia para CHARLES
# Crie uma estratégia para que ALICE receba a autenticação de usuários pela rede.
# A solução deve ser imune a ataques de REPETIÇÃO (REPLAY)
# ALICE tem uma base de senhas cadastradas
senhas = { #dicionario
 'BOB' : 'bf910c5f4e786aca1a5a73f68c77925a',
 'MOE' : 'SENHA',
 'LARRY' : 'OPA',
 'CURLY' : 'YAHOO'
} #keys #values
salt = { #o salt é o nonce que nunca muda
 'BOB': b'mYC+7BjyE/eNq+A0GwoQCA==' 
}
print('ESTA TELA PERTENCE A ALICE')
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 9999))
while True:
# 1) ALICE AGUARDA UM PEDIDO DE LOGIN
 print('Aguardando solicitação de LOGIN ...')
 
 data, addr = s.recvfrom(1024) 
 print('RECEBI: ', data)
 msg = HL.separaMensagem(data) 
 if len(msg) < 2 or msg[0] != 'HELLO': 
 print('recebi uma mensagem inválida')
 continue
 else:
 user = msg[1]
 user_addr = addr
 if user not in senhas.keys():
 print('Usuario desconhecido')
 continue
# 2) ALICE responde ao HELLO com um CHALLENGE 
# -- troque string NONCE por um nonce em formato base64 convertido para string 
(decode)
 #data = HL.formataMensagem(['CHALLENGE', 'NONCE'])
 cs, cs64 = HL.geraNonce(128)
 cs_ALICE = cs64.decode()
 data = HL.formataMensagem(['CHALLENGE', cs_ALICE,salt[user].decode()])
 s.sendto(data, addr )
 if addr != HL.CHARLES: s.sendto(data, HL.CHARLES ) # essa linha simula a ação 
do MALWARE, escuta informacao, charles nao escuta a sim mesmo por isso !=
# 3) ALICE recebe a resposta do CHALLENGE
# -- é preciso separar os componentes da mensagem 
 data, addr = s.recvfrom(1024)
 print('RECEBI: ', data)
 if addr != user_addr:
 print('mensagem de origem desconhecida')
 continue
 msg = HL.separaMensagem(data) 
 if len(msg) < 3 or msg[0] != 'CHALLENGE_RESPONSE': 
 print('recebi uma mensagem inválida')
 continue #volta pro inicio
 else:
 cs_BOB = msg[1]
 hash_BOB = msg[2]
# 4) ALICE verifica se a senha está correta
# -- e preciso calcular o local_HASH usando a CHALLENGE da Alice
# -- faça a comparação com o HASH da senha com o CHALLENGE
 #local_HASH = senhas[user]
 hash_bytes, hash_string = HL.calculaHASH(senhas[user]+ cs_ALICE) #a ordem eh 
importante, muda o resultado
 local_HASH = hash_string
 if hash_BOB == local_HASH:
 resposta = 'SUCCESS'
 print(f'Este usuário é {user}')
 else:
 resposta = 'FAIL'
 print(f'Ataque detectado: Pedido de LOGIN NEGADO!!!')
 continue # ATENCAO: remova essa linha para fazer o teste de repetição do
HMAC
# -- substitua hash_string pelo hash calculado com a senha e o challenge enviado 
por BOB
 hash_bytes, hash_string = HL.calculaHASH(senhas[user]+ cs_BOB) #a ordem eh 
importante, muda o resultado
 local_HASH = hash_string
 msg = HL.formataMensagem([ resposta, local_HASH ])
 
 s.sendto(msg, addr )
 if addr != HL.CHARLES: s.sendto(msg, HL.CHARLES ) # essa linha simula a ação do
MALWARE
# 5) ALICE envia uma mensagem assinada para BOB
 data = HL.assinaMensagem(f'OLA USUARIO {user} VOCE ESTA AUTENTICADO NA ALICE!',
senhas[user])
 s.sendto(data, addr )
 if addr != HL.CHARLES: s.sendto(data, HL.CHARLES ) # essa linha simula a ação 
do MALWARE