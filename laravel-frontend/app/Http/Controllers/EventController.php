<?php

namespace App\Http\Controllers;

use App\Models\Event; // Assuming your Event model is in App\Models
use Illuminate\Http\Request;

class EventController extends Controller
{
    public function index()
    {
        // Fetch ALL events without any pagination
        $events = Event::all(); // Or Event::get(); if you have specific queries

        return view('events.index', compact('events'));
    }
}
