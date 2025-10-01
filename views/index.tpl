<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GoFetch</title>
    <link rel="stylesheet" href="/static/style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&family=Roboto:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">
</head>
<body>

    <div class="search-container" >
        <img class="logo" src="/static/images/logo.png" alt="GoFetch Logo">
        <form method="GET">
            <input class="keywords" type="text" id="keywords" name="keywords" placeholder="Search GoFetch" required>

            <input class="button submit" type="submit" value="Search">
        </form>
    
        <h1>Word Count</h1>
        <table id="results">
            % if keyword_dict:
                % for word, count in keyword_dict.items():
                <tr>
                    <td>{{word}}</td>
                    <td>{{count}}</td>     
                </tr>
                % end
            % end
        </table>
        
        <h1>Top 20 Most Popular</h1>
        <table id="history">
            % if top_20:
                % for i, (word, count) in enumerate(top_20):
                <tr>
                    <td>{{i+1}}. {{word}}</td>
                    <td>{{count}}</td>     
                </tr>
                % end
            % end
        </table>

    </div>

</body>
</html>