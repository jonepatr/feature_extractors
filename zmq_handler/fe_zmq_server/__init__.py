import zmq
import backports.tempfile
import tempfile
import msgpack
import click
import sys
import traceback



def _construct_msg(msg, success, files=None):
    out = {"success": success, "msg": msg}
    if files:
        out["files"] = files
    return msgpack.dumps(out, use_bin_type=True)

def listen():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        #  Wait for next request from client
        message = socket.recv()
        msg = msgpack.loads(message, raw=False)

        if not msg.get("args"):
            socket.send(_construct_msg("args must be set", False))
            continue

        if not msg.get("command"):
            socket.send(_construct_msg("command must be set", False))
            continue

        arguments = []
        output_files = {}
        with backports.tempfile.TemporaryDirectory() as tmpd:
            for key, value in msg["args"].items():
                if isinstance(value, dict):
                    if "_file" in value["type"]:
                        if not value["extension"].startswith("."):
                            value["extension"] = "." + value["extension"]
                        tmpf = tempfile.NamedTemporaryFile(
                            suffix=value["extension"], dir=tmpd, delete=False
                        )
                        argument_value = tmpf.name

                    if value["type"] == "input_file":
                        tmpf.write(value["data"])
                        tmpf.close()

                    if value["type"] == "output_file":
                        output_files[key] = tmpf.name
                else:
                    argument_value = value

                dashes = "-" if len(key) == 1 else "--"
                arguments.append(dashes + key)
                arguments.append(argument_value)
            try:
                command = cli.commands.get(msg["command"])
                if not command:
                    msg = "'{}' not available. Avaialble commands: {}".format(
                        msg["command"], ", ".join(list(cli.commands.keys()))
                    )
                    socket.send(_construct_msg(msg, False))
                    continue
                result = command(arguments, standalone_mode=False)

                files = {}
                for key, filename in output_files.items():
                    with open(filename, "rb") as f:
                        files[key] = f.read()
                socket.send(_construct_msg(result, True, files=files))
            except click.exceptions.MissingParameter as e:
                socket.send(_construct_msg(e.format_message(), False))
            except click.exceptions.NoSuchOption as e:
                socket.send(_construct_msg(e.format_message(), False))
            except Exception as e:
                ex_type, ex_value, ex_traceback = sys.exc_info()

                # Extract unformatter stack traces as tuples
                trace_back = traceback.extract_tb(ex_traceback)

                # Format stacktrace
                stack_trace = list()

                for trace in trace_back:
                    stack_trace.append(
                        "File : %s , Line : %d, Func.Name : %s, Message : %s"
                        % (trace[0], trace[1], trace[2], trace[3])
                    )

                socket.send(
                    _construct_msg(
                        {
                            "stack_trace": stack_trace,
                            "exception_type": ex_type.__name__,
                            "exception_msg": str(ex_value),
                        },
                        False,
                    )
                )
