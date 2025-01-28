function NoMangaScreen({ setDialogVisibility } : {setDialogVisibility : React.Dispatch<React.SetStateAction<boolean>>}) {
    return (
        <>
            <div className="hero bg-base-200 grow">
                <div className="hero-content text-center">
                    <div className="max-w-md">
                        <h1 className="text-5xl font-bold">Загружай мангу!</h1>
                        <p className="py-6">
                            Достаточно лишь загрузить вашу картинку и наш сервис найдет весь текст.
                        </p>
                        <button className="btn btn-primary" onClick={() => setDialogVisibility(true)}>Загрузить мангу</button>
                    </div>
                </div>
            </div>
        </>
    )
}

export default NoMangaScreen
