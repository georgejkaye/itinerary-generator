from jinja2 import Environment, FileSystemLoader, select_autoescape
from structs import BusTripSegment


def write_output(trip: BusTripSegment):
    template = "templates/index.html"
    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape()
    )
    index = env.get_template("index.html")
    html = index.render(trip=trip)
    with open("output.html", "w") as file:
        file.write(html)
