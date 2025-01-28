import { useEffect, useRef } from "react"

function ImageOpenDialog({isDialogVisible, setDialogVisibility, onClose, setFile} : {isDialogVisible : boolean, setDialogVisibility: React.Dispatch<React.SetStateAction<boolean>>, onClose : () => void, setFile: React.Dispatch<React.SetStateAction<File | null>>}) {
    const dialogRef = useRef<HTMLDialogElement>(null);

    useEffect(() => {
        if(!dialogRef.current) return;
        if (dialogRef.current.hasAttribute("open") && !isDialogVisible) {
            dialogRef.current.close()
        } else if (!dialogRef.current.hasAttribute("open") && isDialogVisible) {
            dialogRef.current.show()
        }
    }, [dialogRef, isDialogVisible])

    function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
        if (!e.currentTarget.files) return;
        setFile(e.currentTarget.files[0]);
        setDialogVisibility(false);
    }

    return (
        <>
            <dialog className="modal" ref={dialogRef}>
                <div className="modal-box">
                    <div className="mx-auto text-center">
                        <h3 className="font-bold text-lg">Загрузка манги</h3>
                    </div>
                    <div className="w-full py-4">
                        <input
                            type="file"
                            className="file-input file-input-bordered file-input-primary max-w-xs mx-auto block"
                            onChange={onFileChange} />
                    </div>
                </div>
                <form method="dialog" className="modal-backdrop">
                    <button className="btn-link" onClick={onClose}>close</button>
                </form>
            </dialog>
        </>
    )
}

export default ImageOpenDialog
