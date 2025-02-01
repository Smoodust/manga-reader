import React, { createRef, useEffect, useState } from "react"
import TextSideBar from "./TextSideBar";
import Bbox from "./Bbox";

function MangaDraw({ file } : {file : File}) {

    const canvasRef = createRef<HTMLCanvasElement>();
    const sourceImageRef = createRef<HTMLImageElement>();
    const [bboxs, setBboxs] = useState<Bbox[] | null>(null);
    const [hoveredIndexBbox, setHoveredIndexBbox] = useState<number | null>(null);
    const [selectedIndexBbox, setSelectedIndexBbox] = useState<number | null>(null);
    const [ids, setIds] = useState<string | null>(null);

    useEffect(() => {
        if (!file) return;

        var data = new FormData();
        data.append('file', file);

        fetch("http://localhost:8001/add", {
            method: "POST",
            body: data
        }).then(response => response.json())
        .then(ids => setIds(ids));
    }, [file])

    useEffect(() => {
        if (!ids) return;

        fetch("http://localhost:8001/detect/"+ids, {
            method: "POST"
        }).then(response => response.json())
        .then(box => setBboxs(box));
    }, [ids])

    function redrawCanvas() {
        if (!sourceImageRef.current) return;
        if (!canvasRef.current) return;
        const ctx = canvasRef.current.getContext("2d");
        if (!ctx) return;
    
        const width = sourceImageRef.current.width;
        const height = sourceImageRef.current.height
    
        canvasRef.current.width = width;
        canvasRef.current.height = height;
    
        ctx.clearRect(0, 0, width, height);
        ctx.drawImage(sourceImageRef.current, 0, 0);
    
        if (!bboxs) return;
    
        bboxs.forEach((value, index) => {
            if (index == hoveredIndexBbox || index == selectedIndexBbox) {
                ctx.strokeStyle = "#03045E";
                ctx.fillStyle = "rgba(3, 4, 94, 0.2)";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.rect(value.x, value.y, value.w, value.h);
                ctx.fill();
                ctx.closePath();
                ctx.strokeRect(value.x, value.y, value.w, value.h);
            } else {
                ctx.strokeStyle = "#03045E";
                ctx.lineWidth = 2;
                ctx.strokeRect(value.x, value.y, value.w, value.h);
            }
        })
    }

    function onMouseHover(e: React.MouseEvent<HTMLCanvasElement, MouseEvent>) {
        e.preventDefault();
        
        if (!canvasRef.current) return;
        const ctx = canvasRef.current.getContext("2d");
        if (!ctx) return;
        if (!bboxs) return;

        var rect = canvasRef.current.getBoundingClientRect(),
        x = (e.clientX - rect.left) * canvasRef.current.width / rect.width,
        y = (e.clientY - rect.top) * canvasRef.current.height / rect.height;

        for (let i = 0; i < bboxs.length; i++) {
            var bbox = bboxs[i];
            if (x >= bbox.x && y >= bbox.y && x <= bbox.x + bbox.w && y <= bbox.y + bbox.h) {
                setHoveredIndexBbox(i);
                return;
            }
        }
        setHoveredIndexBbox(null);
    }

    function onMouseDown(e: React.MouseEvent<HTMLCanvasElement, MouseEvent>) {
        e.preventDefault();
        
        if (!canvasRef.current) return;
        const ctx = canvasRef.current.getContext("2d");
        if (!ctx) return;
        if (!bboxs) return;

        var rect = canvasRef.current.getBoundingClientRect(),
        x = (e.clientX - rect.left) * canvasRef.current.width / rect.width,
        y = (e.clientY - rect.top) * canvasRef.current.height / rect.height;

        for (let i = 0; i < bboxs.length; i++) {
            var bbox = bboxs[i];
            if (x >= bbox.x && y >= bbox.y && x <= bbox.x + bbox.w && y <= bbox.y + bbox.h) {
                setSelectedIndexBbox(i);
                return;
            }
        }
        setSelectedIndexBbox(null);
    }

    useEffect(() => {redrawCanvas()}, [bboxs, hoveredIndexBbox])

    return (
        <div className="bg-base-200 grow w-full overflow-y-auto flex">
            <div className="grow">
                <img src={URL.createObjectURL(file)} ref={sourceImageRef} onLoad={() => {redrawCanvas()}} style={{display: "none"}} />
                <canvas ref={canvasRef} className="block h-full mx-auto" onMouseMove={onMouseHover} onMouseDown={onMouseDown} />
            </div>
            {(selectedIndexBbox != null && ids != null) && 
                <TextSideBar ids={ids} index_text={selectedIndexBbox} />
            }
        </div>
    )
}

export default MangaDraw
