from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from threading import Thread
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
import sys
import time

# Function to modify the document
def modify_doc(doc):
    # Create ColumnDataSource
    source = ColumnDataSource(data=dict(x=[], y=[]))

    # Create a figure
    plot = figure(title="Real-time Streaming Data", x_axis_label='X', y_axis_label='Y')
    plot.line('x', 'y', source=source)

    # Add the plot to the current document
    doc.add_root(plot)

    # Function to read from stdin and update the data source
    def update():
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                if "VTG" in line:
                    print(f"Line: {line}")
                    components = line.strip().split(",")
                    x = float(time.time())
                    y = float(components[5]) # speed
                    print(f"Speed: {y}")
                    new_data = dict(x=[x], y=[y])
                    # source.stream(new_data, rollover=200)
                    doc.add_next_tick_callback(lambda: source.stream(new_data, rollover=200))
            except ValueError:
                pass

    # Start the update thread
    thread = Thread(target=update)
    thread.daemon = True
    thread.start()

    # Set the document title
    doc.title = "Streaming Data Example"

# Create the Bokeh application
app = Application(FunctionHandler(modify_doc))

# Start the Bokeh server
server = Server({'/': app})
server.start()

# Open a session to keep the server alive
if __name__ == '__main__':
    print("Opening Bokeh application on http://localhost:5006/")
    server.io_loop.add_callback(server.show, "/")
    server.io_loop.start()
