
Title "Implementador - Sistema SMMAURB - (c) Carlos A. Locatelli"

for /d /r . %%f in ("__pycache__") do rmdir /s /q "%%f"

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\controllers\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\controllers\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\models\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\models\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\languages\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\languages\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\modules\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\modules\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\views\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\views\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\static\" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\static\" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\VERSION.txt" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\VERSION.txt" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\README.md" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\README.md" /S /E /Y /H /D

xcopy   "%userprofile%\web2py\applications\Qualidade_Ambiental\LICENSE" "F:\SMMAURB\SISTEMA DE DADOS\Qualidade\Qualidade_Ambiental\applications\Qualidade_Ambiental\LICENSE" /S /E /Y /H /D

xcopy "%userprofile%\web2py\site-packages" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\site-packages\" /S /E /Y /H /D

echo 'ISNTALAÇÃO FINALIZADA-';


PAUSE
