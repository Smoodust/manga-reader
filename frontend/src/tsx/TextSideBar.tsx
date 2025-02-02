import { useEffect, useRef } from "react"

function TextSideBar({ ids, index_text } : { ids: string, index_text: number }) {

    const transcriptionRef = useRef<HTMLParagraphElement>(null);

    useEffect(() => {
        fetch("http://localhost:8000/api/ocr/"+ids+"/"+index_text, {
            method: "POST"
        }).then(response => response.json())
        .then(text => {
            if (!transcriptionRef.current) return;
            transcriptionRef.current.innerHTML = text
        });
    }, [ids, index_text]);

    return (
        <>
            <aside className="basis-1/4">
                <h2 className="text-3xl font-bold p-4">Транскрипция</h2>
                <p className="text-xg p-4" ref={transcriptionRef}><span className="loading loading-spinner loading-xs"></span></p>
            </aside>
        </>
    )
}

export default TextSideBar
