$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    foreach ($volume in 1..3) {
        $jobName = 'volume-{0:D2}' -f $volume
        $texInput = '\def\CoverVolume{' + $volume + '}\input{preview.tex}'
        foreach ($pass in 1..2) {
            & xelatex -interaction=nonstopmode -halt-on-error "-jobname=$jobName" $texInput
            if ($LASTEXITCODE -ne 0) { throw "封面 $volume 第 $pass 遍编译失败，请查看 $jobName.log。" }
        }
        if (Get-Command pdftoppm -ErrorAction SilentlyContinue) {
            & pdftoppm -scale-to 1200 -png "$jobName.pdf" $jobName
            if ($LASTEXITCODE -ne 0) { throw "封面 $volume 预览导出失败。" }
        }
    }
} finally {
    Pop-Location
}
