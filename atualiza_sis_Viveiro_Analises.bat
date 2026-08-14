
Title "Implementador - Sistema SMMAURB - (c) Carlos A. Locatelli"


robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\controllers" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\controllers" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\models" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\models" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\languages" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\languages" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\modules" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\modules" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\views" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\views" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\static" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\static" /E /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises" README.md  /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises" LICENSE /XO

robocopy    "%userprofile%\web2py\applications\Viveiro_Analises\private" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\applications\Viveiro_Analises\private" appconfig.json /XO

robocopy    "%userprofile%\web2py\site-packages" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises\site-packages" /E /XO

robocopy    "%userprofile%\web2py" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises" atualiza_apps.bat /XO

robocopy    "%userprofile%\web2py" "F:\SMMAURB\SISTEMA DE DADOS\Viveiro\Viveiro_Analises" requirements.txt /XO

echo 'FINALIZADO!';


PAUSE
