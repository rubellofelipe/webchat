import websockets
import asyncio
import json

clients = {}  # {{'nome': nome, 'websocket': websocket}}
# funcoes:  help     -> lista de todos os comandos
#          usuarios -> lista de usuarios
#          nome     -> mudar o nome

server_name = 'server'

global_message = 'all'
target_message = 'target'
command_message = 'command'
alert_message = 'alert'
set_name_message = 'set'


'''
formato padrao de mensagem:
{'sender': nome, 'data': mensagem , 'type': tipo_de_mensagem}
'''


def getid():
    for i in range(len(clients)+1):
        if i in clients.keys():
            continue
        id = i
        break
    return id


def nome_valido(nome):
    for user in clients:
        if nome == '':
            return False
        if len(nome) > 20:
            return False
        if (nome == clients[user]['nome']):
            return False
        if nome == server_name:
            return False

    return True


def get_str_user():
    string = ''
    for client in clients:
        string += '@' + clients[client]['nome'] + '\n'
    return string.strip('\n')


def get_list_user():
    lista = []
    for client in clients:
        lista.append(clients[client]['nome'])
    return lista


async def broad(msg, id):
    for client in clients:
        if client != id:
            await clients[client]['websocket'].send(msg)


async def target(id, alvo, msg):
    if clients[id]['nome'] == alvo:
        await clients[id]['websocket'].send(json.dumps({'sender': server_name, 'data': 'Você está mandando mensagem privada para si mesmo', 'type': alert_message}))

    elif alvo in get_list_user():
        for client in clients:
            if clients[client]['nome'] == alvo:
                await clients[client]['websocket'].send(msg)
    else:
        await clients[id]['websocket'].send(json.dumps({'sender': server_name, 'data': 'O usuário especifícado não existe. Utilize \\usuarios para ver quem está na sala', 'type': alert_message}))


async def command(id, func, par):
    if func == 'help':
        msg = json.dumps(
            {'sender': server_name, 'data': 'funcções disponíveis:\n\\help\n\\usuarios\n\\nome', 'type': command_message})
        await clients[id]['websocket'].send(msg)
    elif func == 'usuarios':
        list_user = get_str_user()
        msg = json.dumps(
            {'sender': server_name, 'data': f'os usuários na sala sâo:\n{list_user}', 'type': command_message})
        await clients[id]['websocket'].send(msg)
    elif func == 'nome':
        if nome_valido(par):
            set_name = json.dumps(
                {'sender': server_name, 'data': f'seu nome : {par}', 'type': set_name_message})
            await clients[id]['websocket'].send(set_name)
            warn_message = json.dumps(
                {'sender': server_name, 'data': f'o usuário {clients[id]["nome"]} mudou para o nome {par}', 'type': alert_message})
            await broad(warn_message, id)
            clients[id]['nome'] = par
        else:
            msg = json.dumps(
                {'sender': server_name,
                 'data': 'Novo nome inválido', 'type': alert_message})
            await clients[id]['websocket'].send(msg)
        print('nome')
    else:
        print(f'a função {func} não é válida')
        sendhash = json.dumps(
            {'sender': 'server', 'data': f'a função {func} não é válida. digite \\help para ver a lista de funções disponíveis', 'type': alert_message})
        await clients[id]['websocket'].send(sendhash)


async def echo(websocket, path):
    try:

        nome = ''
        mensagem = {'sender': server_name,
                    'data': 'Envie o seu nome', 'type': alert_message}
        msg = json.dumps(mensagem)
        await websocket.send(msg)
        msg = await websocket.recv()
        mensagem = json.loads(msg)
        nome = mensagem['data']
        while not nome_valido(nome):
            msg = json.dumps(
                {'sender': server_name,
                 'data': 'Nome invalido. Envie um novo nome', 'type': alert_message})
            await websocket.send(msg)
            msg = await websocket.recv()
            mensagem = json.loads(msg)
            nome = mensagem['data']

        id = getid()
        clients[id] = {'nome': nome, 'websocket': websocket}
        set_name = json.dumps(
            {'sender': server_name, 'data': f'seu nome : {nome}', 'type': set_name_message})
        await websocket.send(set_name)
        msg = json.dumps(
            {'sender': server_name, 'data': f'o usuário {nome} entrou na sala', 'type': alert_message})
        await broad(msg, id)

        while True:
            gethash = await websocket.recv()
            informacao = json.loads(gethash)
            message_sender = informacao['sender']
            message = informacao['data']

            if message[0] == '@':  # mensagem privada
                try:
                    index = message.index(' ')
                    alvo = message[1:index]
                    message = message[index+1:]
                    sendhash = json.dumps(
                        {'sender': clients[id]["nome"], 'data': message, 'type': target_message})
                    await target(id, alvo, sendhash)
                except:
                    sendhash = json.dumps(
                        {'sender': server_name, 'data': 'não foi mandado nenhuma mensagem', 'type': alert_message})
                    await websocket.send(sendhash)

            elif message[0] == "\\":  # comando para o servidor
                if ' ' in message:
                    k = message.index(' ')
                    func = message[1:k]
                    par = message[k+1:]
                else:
                    func = message[1:]
                    par = None

                await command(id, func, par)

            else:  # mensagem para todos
                sendhash = json.dumps(
                    {'sender': clients[id]["nome"], 'data': message, 'type': global_message})
                await broad(sendhash, id)
    except:
        print(
            f'o usuário de id {id} e nome {clients[id]["nome"]} foi desconectado')
        sendhash = json.dumps(
            {'sender': server_name, 'data': f'o usário {clients[id]["nome"]} foi desconectado', 'type': alert_message})
        await broad(sendhash, id)
        del clients[id]


start_server = websockets.serve(echo, "localhost", 8888)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
