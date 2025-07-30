@extends('layouts.app')

@section('content')
<div class="container mt-5">
    <h1 class="mb-4">📅 Upcoming Events</h1>

    @forelse ($events as $event)
        <div class="card mb-4 shadow-sm">
            <div class="card-body">
                <h5 class="card-title">{{ $event->title }}</h5>

                @if ($event->date_string)
                    <p><strong>Date:</strong> {{ $event->date_string }}</p>
                @endif

                @if ($event->location)
                    <p><strong>Location:</strong> {{ $event->location }}</p>
                @endif

                @if ($event->organizer)
                    <p><strong>Organizer:</strong> {{ $event->organizer }}</p>
                @endif

                @if ($event->price)
                    <p><strong>Price:</strong> {{ $event->price }}</p>
                @endif

                @if ($event->description)
                    <p class="text-muted">{{ Str::limit($event->description, 200) }}</p>
                @endif

                <a href="{{ $event->source_url }}" target="_blank" class="btn btn-primary">🔗 View Original</a>
            </div>
        </div>
    @empty
        <div class="alert alert-warning">No events found.</div>
    @endforelse

    {{-- Pagination has been removed to display all events on a single page --}}
</div>
@endsection
