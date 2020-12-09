import requests
from tkinter import *
from tkinter import ttk
from io import BytesIO
from PIL import ImageTk, Image
import asyncio
import aiohttp


async def download_image(session, image):
    async with session.get(image["iconimage"]) as response:
        if response.status == 200:
            image["iconimage"] = await response.read()
            return image


def get_icons_data(query):
    print("Searching for query: " + query)
    r = requests.get(
        "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/summoner-icons.json"
    ).json()
    liste = []
    for x in r:
        if query.lower() in x["title"].lower():
            dictionary = {
                "iconid": x["id"],
                "iconname": x["title"],
                "iconreleaseyear": x["yearReleased"],
                "iconimage": (
                    "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
                    + str(x["id"])
                    + ".jpg"
                ),
            }
            try:
                dictionary["icondescription"] = x["descriptions"][0]["description"]
            except IndexError:
                dictionary["icondescription"] = ""
            liste.append(dictionary)
    return liste


def set_clipboard(id):
    print("Adding " + str(id) + " to clipboard.")
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(id)
    r.update()
    r.destroy()


def on_mousewheel(event, canvas):
    shift = (event.state & 0x1) != 0
    scroll = -1 if event.delta > 0 else 1
    if shift:
        canvas.xview_scroll(scroll, "units")
    else:
        canvas.yview_scroll(scroll, "units")


def open_in_browser(id):
    import webbrowser

    webbrowser.open(
        f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{id}.jpg",
        new=2,
    )


def show_results(master, responses, query):
    master.destroy()
    master = Tk()
    master.iconbitmap("icon.ico")
    master.title("Search results for query: " + str(query))
    master.geometry("800x1000")
    master.resizable(True, False)
    canvas = Canvas(master)
    scroll_y = Scrollbar(master, orient="vertical", command=canvas.yview)
    frame = Frame(canvas)
    for response in responses:
        if response == None:
            continue
        Label(frame, text=response["iconname"], font="-weight bold").pack()
        Label(frame, text="ID: " + str(response["iconid"])).pack()
        Label(frame, text="Description: " + response["icondescription"]).pack()
        Label(frame, text="Released in: " + str(response["iconreleaseyear"])).pack()
        img = ImageTk.PhotoImage(Image.open(BytesIO(response["iconimage"])))
        label = Label(frame, image=img)
        label.img = img
        label.pack()
        idbutton = Button(
            frame,
            text="Copy ID to Clipboard",
            command=lambda id=response["iconid"]: set_clipboard(id),
        )
        idbutton.pack(fill="x", pady="5")
        linkbutton = Button(
            frame,
            text="Open image link",
            command=lambda id=response["iconid"]: open_in_browser(id),
        )
        linkbutton.pack(fill="x", pady="5")
        ttk.Separator(frame, orient=HORIZONTAL).pack(fill="x", pady="10")
    canvas.create_window(0, 0, anchor="nw", window=frame)
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"), yscrollcommand=scroll_y.set)
    canvas.pack(fill="both", expand=True, side="left")
    scroll_y.pack(fill="y", side="right")
    Button(
        master, text="Restart search", command=lambda: [master.destroy(), search()]
    ).pack(side="right", fill="y")
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))
    master.mainloop()


async def create_downloads(liste, progress, master, progressLabel):
    async with aiohttp.ClientSession() as session:  # create aiohttp session
        tasks = [
            download_image(session, image) for image in liste  # Create list of tasks
        ]
        responses = []
        progress["value"] = 0
        totalTasks = len(tasks)
        for count, t in enumerate(asyncio.as_completed(tasks)):
            progressLabel["text"] = f"Completed: {count} of {totalTasks}"
            master.update()
            progress.step()
            responses.append(await t)
        return responses


def progress_window(liste, query, master):
    master.destroy()
    if liste == []:
        print("No icons found.")
        search()
        return
    master = Tk()
    master.iconbitmap("icon.ico")
    master.title(f"Downloading icons for query: {query}")
    master.resizable(False, False)
    progress = ttk.Progressbar(
        master=master,
        orient="horizontal",
        length=500,
        mode="determinate",
        maximum=len(liste),
    )
    progress.pack()
    progressLabel = Label()
    progressLabel.pack()
    master.update()

    show_results(
        master,
        asyncio.get_event_loop().run_until_complete(
            create_downloads(liste, progress, master, progressLabel)
        ),
        query,
    )
    master.mainloop()


def search():
    master = Tk()
    master.iconbitmap("icon.ico")
    master.title("Search")
    master.geometry("500x100")
    master.resizable(False, False)
    Label(master, text="Search query: ").pack()
    e = Entry(master, justify="center")
    e.pack(pady="10", fill="x")

    button = Button(
        master,
        text="Search",
        command=lambda: [progress_window(get_icons_data(e.get()), e.get(), master)],
    )
    button.pack(fill="x", side="bottom")
    master.bind("<Return>", lambda event=None: button.invoke())
    master.mainloop()


search()
