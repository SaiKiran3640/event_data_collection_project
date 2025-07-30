<?php

use App\Http\Controllers\EventController;

Route::get('/events', [EventController::class, 'index']);
