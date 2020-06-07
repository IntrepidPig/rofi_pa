import sys
import subprocess

# Set the default sink and move all streams to the sink specified
# by `sink`.
def set_sink(name):
    _set_item("sink", name)

# Set the default source and move all streams to the source specified
# by `name`.
def set_source(name):
    _set_item("source", name)

def _set_item(item, name):
    run_pacmd_cmd(["set-default-{}".format(item), name])
    for line in run_pacmd_cmd(["list-{}-inputs".format(item)]).splitlines():
        if "index" in line:
            stream_index = line.split()[-1]
            run_pacmd_cmd(["move-{}-input".format(item), stream_index, name])

# Returns a list of all available sink names
def list_sinks():
    return _list_items("sink")

# Returns a list of all available source names
def list_sources():
    return _list_items("source")

# Return the name of the default sink
def get_default_sink():
    return _get_default_item("sink")

# Return the name of the default source
def get_default_source():
    return _get_default_item("source")

def _get_default_item(item):
    items = run_pacmd_cmd(["list-{}s".format(item)])
    lines = items.splitlines()
    for i in range(len(lines)):
        if "index" in lines[i]:
            if lines[i].split()[0] == "*":
                return lines[i+1].split()[-1][1:-1]

def _list_items(item):
    return list(map(lambda x: x.split()[-1][1:-1], filter(lambda x: "name:" in x, run_pacmd_cmd(["list-{}s".format(item)]).splitlines())))

# Run a pacmd process with the arguments given and return stdout
def run_pacmd_cmd(args):
    args = ["pacmd"] + args
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.poll() != 0:
        raise Exception("pacmd execution failed. stdout:\n{}\nstder:\n{}".format(stdout, stderr))
    return stdout.decode("utf-8")

def run_rofi_output(item):
	table = {
		"sink": (get_default_sink, list_sinks, set_sink, "output"),
		"source": (get_default_source, list_sources, set_source, "input")
	}
	get_default, list_items, set_item, prompt = table[item]
	
	print("\0prompt\x1f{}".format(prompt))
	if len(sys.argv) == 1:
		default = get_default()
		for i, name in enumerate(list_items()):
			if name == default:
				print("\0active\x1f{}".format(i))
			print(name)
	else:
		set_item(sys.argv[1])