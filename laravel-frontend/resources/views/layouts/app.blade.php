<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Event Viewer</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        /* Custom CSS to hide the "Previous" and "Next" pagination buttons */
        .pagination .page-item:first-child, /* Targets the "Previous" button */
        .pagination .page-item:last-child {  /* Targets the "Next" button */
            display: none !important; /* Hides the entire list item */
        }

        /* General styling for numeric page links (optional, can be adjusted) */
        .pagination .page-link {
            padding: 0.25rem 0.5rem; /* Smaller padding for links */
            font-size: 0.75rem; /* Smaller font size for link text */
            line-height: 1.5; /* Standard line height for text */
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ url('/events') }}">Event Viewer</a>
        </div>
    </nav>

    <main class="container">
        @yield('content')
    </main>

    <footer class="text-center mt-4 mb-2 text-muted">
        <small>© {{ date('Y') }} Event Viewer</small>
    </footer>
</body>
</html>