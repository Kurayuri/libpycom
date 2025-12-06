import zmq

class ZmqCCL:
    @staticmethod
    def broadcast(rank, world_size, src, data):
        context = zmq.Context()
        if rank == src:
            print(f"Rank {rank}: Generated Unique ID")
            socket = context.socket(zmq.REP)
            socket.bind("tcp://*:5555") 
            
            for i in range(world_size - 1):
                msg = socket.recv()
                client_rank = int(msg.decode())
                print(f"Rank {src}: Received request from Rank {client_rank} ({i+1}/{world_size-1})")
                socket.send(data)
            socket.close()
            context.term()
            return data
        else:
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://localhost:5555") 
            socket.send(str(rank).encode())

            data = socket.recv()
            print(f"Rank {rank}: Received")
            
            socket.close()
            context.term()
            return data
