import { useState } from "react"
import ImageOpenDialog from "./ImageOpenDialog";
import NoMangaScreen from "./NoMangaScreen";
import MangaDraw from "./MangaDraw";

function Main() {
    const [dialogVisibility, setDialogVisibility] = useState(false);
    const [file, setFile] = useState<File | null>(null);

    function onCloseDialog() {
        setDialogVisibility(false);
    }

    return (
        <>
            <div className="h-screen w-screen flex flex-col">
                <div className="navbar bg-base-100">
                    <div className="flex-1">
                        <a className="btn btn-ghost text-xl">MangaOCR</a>
                    </div>
                    <div className="flex-none">
                        <button className="btn btn-ghost" onClick={() => setDialogVisibility(true)}>Загрузить мангу</button>
                    </div>
                </div>
                {
                    !file ? <NoMangaScreen setDialogVisibility={setDialogVisibility} /> : <MangaDraw file={file} />
                }
            </div>
            <ImageOpenDialog isDialogVisible={dialogVisibility} setDialogVisibility={setDialogVisibility} onClose={onCloseDialog} setFile={setFile} />
        </>
    )
}

export default Main
