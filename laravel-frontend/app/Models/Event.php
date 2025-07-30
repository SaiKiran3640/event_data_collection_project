<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Event extends Model
{
    protected $table = 'events';

    protected $fillable = [
        'title',
        'date_string',
        'location',
        'description',
        'organizer',
        'price',
        'source_url',
        'scraped_at',
        'created_at',
        'updated_at',
    ];

    public $timestamps = true;
}
