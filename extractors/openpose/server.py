import fe_zmq_server
import extract

if __name__ == "__main__":
    fe_zmq_server.listen(extract.cli)