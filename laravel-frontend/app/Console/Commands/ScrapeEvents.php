<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Event;

class ScrapeEvents extends Command
{
    protected $signature = 'events:scrape';
    protected $description = 'Scrapes events and saves them to the database';

    public function handle()
    {
        // Dummy data for now
        Event::create([
            'title' => 'Sample Event',
            'source_url' => 'https://example.com',
            'date' => now(),
            'location' => 'Hyderabad',
            'description' => 'This is a sample event.',
            'organizer' => 'ABC Corp'
        ]);

        $this->info('Events scraped and saved successfully!');
    }
}

