



Error_Dictionary= {

    "1" : "Missing Files",
    "2" : "Scientific Calculation Error",
    "3" : "Calculator Error",
    "4" : "UI Error",
    "5" : "Configuration Error",
    "6" : "Communication Error",
    "7" : "Runtime Error"

}

#Error Messages are structured in:
# 1. Digit: Main Error
# 2. Digit: Specification
# 3. and 4. Digit: Error Number



ERROR_MESSAGES = {
    "2000" : "Sin/Cos/tan was recognized, but couldnt be assigned in processing.",
    "2001" : "Logarithm Syntax.",
    "2002" : "Invalid Number or Base in Logarithm.",
    "2003" : "Logarithm result error: ", # + Calculated Result
    "2004" : "Unable to identify given Operation: ", # + Given Problem
    "2505" : "Loading Configurations for degree setting.",
    "2706" : "Process already running",


    "3000" : "Missing Opening Bracket: ", # + Given Problem
    "3001" : "Missing Solver.",
    "3002" : "Multiple Variables in problem: ", # + Given Problem
    "3003" : "Division by Zero",
    "3004" : "Invalid Operator: ", # + operator
    "3005" : "Non linear problem. ",
    "3006" : "Non linear problem (Division by Variable)",
    "3007" : "Non linear problem (Potenz)",
    "3008" : "More than one '.' in one number.",
    "3009" : "Missing ')'. ",
    "3010" : "Missing '('. ",
    "3011" : "Unexpected Token: ", # + Token
    "3012" : "Invalid equation:  ", # + Equation
    "3013" : "Infinit Solutions.",
    "3014" : "No Solution",
    "3015" : "Normal Calculator on Equation.",
    "3216" : "Missing ')' after Logarithm base.",
    "3217" : "Missing ')' after function",
    "3218" : "Error with Scientific function: ", #+Problem
    "3219" : "π",
    "3720" : "'=' in collect_terms",
    "3721" : "Process already running",


    "4700" : "Process already running",
    "4501" : "Not all Settings could be saved: ", # + Error raising setting
    "4002" : "Calculation already Running!",



    "5000" : ""
}
