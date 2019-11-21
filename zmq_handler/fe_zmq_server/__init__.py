import zmq
import backports.tempfile
import tempfile
import msgpack
import sys
import traceback
import click
import tarfile
import os
from uuid import uuid4

try:
    from cStringIO import StringIO as BIO
except ImportError:  # python 3
    from io import BytesIO as BIO


def _construct_msg(msg, success, files=None):
    out = {"success": success, "msg": msg}
    if files:
        out["files"] = files

    return msgpack.dumps(out, use_bin_type=True)


def listen(cli, port=5555):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:{}".format(port))

    while True:
        #  Wait for next request from client
        message = socket.recv()
        msg = msgpack.loads(message, raw=False)

        if "args" not in msg:
            socket.send(_construct_msg("args must be set", False))
            continue

        if "command" not in msg:
            socket.send(_construct_msg("command must be set", False))
            continue

        arguments = []
        output_files = {}
        with backports.tempfile.TemporaryDirectory() as tmpd:
            for key, value in msg["args"].items():
                if isinstance(value, dict):
                    if value.get("extension") and not value["extension"].startswith(
                        "."
                    ):
                        value["extension"] = "." + value["extension"]

                    if value["type"] == "input_file":
                        tmpf = tempfile.NamedTemporaryFile(
                            suffix=value["extension"], dir=tmpd, delete=False
                        )
                        tmpf.write(value["data"])
                        tmpf.close()
                        argument_value = tmpf.name

                    if "output_" in value["type"]:
                        base_name = os.path.join(tmpd, str(uuid4()))
                        name_w_extension = base_name + value.get("extension", "")

                    if value["type"] == "output_file":
                        output_files[key] = {"name": name_w_extension, "type": "file"}
                        argument_value = name_w_extension
                    elif value["type"] == "output_dir":
                        output_files[key] = {
                            "name": base_name,
                            "tar": name_w_extension,
                            "type": "dir",
                        }
                        argument_value = base_name
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
                for key, out_file in output_files.items():
                    if out_file["type"] == "file":
                        with open(out_file["name"], "rb") as f:
                            files[key] = f.read()
                    elif out_file["type"] == "dir":
                        file_out = BIO()
                        with tarfile.open(mode="w", fileobj=file_out) as tar:
                            tar.add(
                                out_file["name"],
                                arcname=os.path.basename(out_file["name"]),
                            )
                        file_out.seek(0)
                        files[key] = file_out.read()

                socket.send(_construct_msg(result, True, files=files))
            except click.exceptions.MissingParameter as e:
                socket.send(_construct_msg(e.format_message(), False))
            except click.exceptions.NoSuchOption as e:
                socket.send(_construct_msg(e.format_message(), False))
            except Exception as e:
                ex_type, ex_value, ex_traceback = sys.exc_info()
                trace_back = traceback.extract_tb(ex_traceback)
                stack_trace = []
                for trace in trace_back:
                    stack_trace.append(
                        {
                            "file": trace[0],
                            "line": trace[1],
                            "func_name": trace[2],
                            "message": trace[3],
                        }
                    )
                error_msg = {
                    "stack_trace": stack_trace,
                    "exception_type": ex_type.__name__,
                    "exception_msg": str(ex_value),
                }
                socket.send(_construct_msg(error_msg, False,))
