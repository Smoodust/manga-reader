function MangaDraw({ file } : {file : File}) {
    return (
        <>
            <div className="bg-base-200 grow w-full overflow-y-auto">
                <img src={URL.createObjectURL(file)} className="block h-full mx-auto" />
            </div>
        </>
    )
}

export default MangaDraw
