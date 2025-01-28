function MangaDraw({ file } : {file : File}) {
    return (
        <>
            <img src={URL.createObjectURL(file)} />
        </>
    )
}

export default MangaDraw
