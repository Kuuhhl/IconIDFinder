import requests
from tkinter import *
import tkinter.ttk
from io import BytesIO
from PIL import ImageTk, Image
import urllib


def get_icons(query):
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
                "iconlegacy": x["isLegacy"],
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
    r.update()  # now it stays on the clipboard after the window is closed
    r.destroy()


def show_results(liste, master, query):
    print("Searching for query: " + query)
    master.destroy()
    if liste == []:
        print("No icons found.")
        search("")
        return
    master = Tk()
    master.iconbitmap("icon.ico")
    master.title("Search results for: " + str(query))
    master.geometry("570x1000")
    master.resizable(True, False)
    canvas = Canvas(master)
    scroll_y = Scrollbar(master, orient="vertical", command=canvas.yview)
    frame = Frame(canvas)
    for x in liste:
        print("Icon found: " + x["iconname"])
        Label(frame, text=x["iconname"]).pack()
        Label(frame, text="ID: " + str(x["iconid"])).pack()
        Label(frame, text="Description: " + x["icondescription"]).pack()
        Label(frame, text="Released in: " + str(x["iconreleaseyear"])).pack()
        Label(frame, text="Legacy: " + str(x["iconlegacy"])).pack()
        try:
            img = (
                ImageTk.PhotoImage(
                    Image.open(
                        BytesIO(
                            urllib.request.urlopen(
                                urllib.request.Request(
                                    x["iconimage"], headers={"User-Agent": "Mozilla"}
                                )
                            ).read()
                        )
                    )
                ),
            )

            label = Label(frame, image=img)
            label.img = img
            label.pack()
        except urllib.error.HTTPError:
            pass
        idbutton = Button(
            frame,
            text="Copy ID to Clipboard",
            command=lambda id=x["iconid"]: set_clipboard(id),
        )
        idbutton.pack(fill="x", pady="5")
        tkinter.ttk.Separator(frame, orient=HORIZONTAL).pack(fill="x", pady="10")

    canvas.create_window(0, 0, anchor="nw", window=frame)
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"), yscrollcommand=scroll_y.set)
    canvas.pack(fill="both", expand=True, side="left")
    scroll_y.pack(fill="y", side="right")
    Button(master, text="Restart search", command=lambda: search(master)).pack(
        side="right", fill="y"
    )
    print("Finished searching.")


def search(master):
    try:
        master.destroy()
    except:
        pass
    master = Tk()
    master.iconbitmap("icon.ico")
    master.title("Search")
    master.geometry("500x100")
    master.resizable(False, False)
    Label(master, text="Search query: ").pack()
    e = Entry(master, justify="center")
    e.pack(pady="10", fill="x")
    e.focus_set()

    button = Button(
        master,
        text="Search",
        command=lambda: show_results(get_icons(e.get()), master, e.get()),
    )
    button.pack(fill="x", side="bottom")
    master.bind("<Return>", lambda event=None: button.invoke())
    master.mainloop()


search("")
