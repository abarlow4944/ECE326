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
        <!-- Top Bar -->
        <div class="top-bar">
            % if logged_in:
                <p class= "welcome">Welcome, {{ user_email }}</p>
                <a href="/logout" class="sign-out button">Sign out</a>
            % else:
                <a href="/signin" class="sign-in button">Sign in</a>
            % end
        </div>

        <!--  Search Bar -->
        <img class="logo" src="/static/images/logo.png" alt="GoFetch Logo">

        <form action="/search" method="GET">
            <input class="keywords" type="text" id="keywords" name="keywords" placeholder="Search GoFetch" required>

            <input class="button submit" type="submit" value="Search">
        </form>

        <!-- Tables -->
        <div class="tables-container">
        <div class="table">
            <table id="results">
                <th colspan="2">Word Count</th>
                % if keyword_dict:
                    % for word, count in keyword_dict.items():
                    <tr>
                        <td>{{word}}</td>
                        <td>{{count}}</td>     
                    </tr>
                    % end
                % end
            </table>
        </div>
        
        <div class="table">
            <table id="history">
                <th colspan="2">Top 20 Most Popular</th>
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

        <!-- only logged in users have access -->
        % if logged_in:
        <div class="table">
            <table id="recent">
                <th colspan="2">Recent Searches</th>
                % if recent:
                    % for keyword in recent:
                    <tr>
                        <td>{{ keyword }}</td>
                    </tr>
                    % end
                % end
            </table>
        </div>
        % end
    </div>

    </div>

    <div class="results-container">
        <!-- Results -->
        % if len(results) > 0:
            % for result in results:
                <div class="results-bundle">
                    <a class="result-title" href="{{result['url']}}" target="_blank">
                        <h1>{{result['title']}}</h1>
                    </a>
                    <p class="result-desc">{{result['desc']}}</p>
                </div>
            % end

            <!-- Pagination -->
            <div class="pagination">
                <div class="pagination-buttons">
                        
                    % if page > 1:
                        <a class="button" href="/search?keywords={{query}}&page={{page-1}}">Previous</a>
                    % end
                    <span>Page {{page}}</span>
                    % if results and len(results) >= 5:  
                        <a class="button" href="/search?keywords={{query}}&page={{page+1}}">Next</a>
                    % end

                </div>
            </div>

        <!-- Error Message -->
        % elif query:
            <p class="no-results">No results found for "{{query}}".</p>
        % end
    </div>

</body>
</html>