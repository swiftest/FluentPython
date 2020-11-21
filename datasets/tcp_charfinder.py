import sys
import asyncio

from charfinder import UnicodeNameIndex  

CRLF = b'\r\n'
PROMPT = b'?> '

index = UnicodeNameIndex()  

async def handle_queries(reader, writer):  
    while True:  
        writer.write(PROMPT)  
        await writer.drain() 
        data = await reader.readline() 
        try:
            query = data.decode().strip()
        except UnicodeDecodeError:
            query = '\x00'
        client = writer.get_extra_info('peername')  
        print('Received from {}: {!r}'.format(client, query))  
        if query:
            if ord(query[:1]) < 32:  
                break
            lines = list(index.find_description_strs(query)) 
            if lines:
                writer.writelines(line.encode() + CRLF for line in lines) 
            writer.write(index.status(query, len(lines)).encode() + CRLF)

            await writer.drain() 
            print('Sent {} results'.format(len(lines))) 

    print('Close the client socket')  
    writer.close() 
# END TCP_CHARFINDER_TOP


# BEGIN TCP_CHARFINDER_MAIN
async def main(address='127.0.0.1', port=2323):  
    port = int(port)
    server = await asyncio.start_server(handle_queries, address, port) 

    host = server.sockets[0].getsockname() 
    print('Serving on {}. Hit CTRL-C to stop.'.format(host))  

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main(*sys.argv[1:]))
    except KeyboardInterrupt:
        pass
    
    print('\nServer shutting down.')
    