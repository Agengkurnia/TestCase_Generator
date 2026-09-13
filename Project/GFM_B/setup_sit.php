<?php

require 'D:/Work/Source/Dashboard-Slope-GFM/vendor/autoload.php';
$app = require 'D:/Work/Source/Dashboard-Slope-GFM/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

use App\Models\Inspection;
use App\Models\Module;
use App\Models\Role;
use App\Models\RoleAccess;
use App\Models\Slope;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

function user(string $email, string $name, ?string $role): void
{
    $user = User::query()->updateOrCreate(
        ['email' => $email],
        ['name' => $name, 'password' => Hash::make('password')]
    );
    $user->roles()->detach();
    if ($role) {
        $user->assignRoleByCode($role);
    } else {
        $user->flushAccessCache();
    }
}

user('sit.admin@gfm.test', 'SIT Admin', 'admin');
user('sit.viewer@gfm.test', 'SIT Viewer', 'viewer');
user('sit.none@gfm.test', 'SIT No Access', null);

$dual = User::query()->updateOrCreate(
    ['email' => 'sit.dual@gfm.test'],
    ['name' => 'SIT Dual Role', 'password' => Hash::make('password')]
);
$dual->roles()->detach();
$dual->assignRoleByCode('admin');
$dual->assignRoleByCode('viewer');

$inspectorRole = Role::query()->updateOrCreate(
    ['code' => 'sit_inspector'],
    [
        'name' => 'SIT Inspector',
        'description' => 'Inspection view+create, bukan langkah approval',
        'is_superuser' => false,
        'is_active' => true,
    ]
);
$flag = ['can_view' => false, 'can_create' => false, 'can_edit' => false, 'can_delete' => false];
foreach (['dashboard' => ['can_view' => true], 'inspection' => ['can_view' => true, 'can_create' => true]] as $code => $perms) {
    $moduleId = Module::query()->where('code', $code)->value('id');
    RoleAccess::query()->updateOrCreate(
        ['role_id' => $inspectorRole->id, 'module_id' => $moduleId],
        array_merge($flag, $perms)
    );
}
user('sit.inspector@gfm.test', 'SIT Inspector', 'sit_inspector');

$seeds = [
    ['SIT-HIGH', 'sit-high', 'cut-type', ['IS' => 1, 'CS' => 20000, 'TS' => 20000, 'RS' => 1260], 'A'],
    ['SIT-MED', 'sit-med', 'cut-type', ['IS' => 1, 'CS' => 2000, 'TS' => 2000, 'RS' => 126], 'B'],
    ['SIT-LOW', 'sit-low', 'rock-type', ['IS' => 1, 'CS' => 1, 'TS' => 1, 'RS' => 0.022], 'A'],
];

foreach ($seeds as [$name, $slug, $type, $ranking, $side]) {
    Slope::query()->updateOrCreate(
        ['slug' => $slug],
        [
            'slope_name' => $name,
            'location' => 'KM SIT',
            'sta1' => '0+000',
            'sta2' => '0+100',
            'latitude' => '-7.1',
            'longtitude' => '110.4',
            'side_of_road' => $side,
            'slope_type' => $type,
            'ranking' => $ranking,
            'geometry' => ['feature_height' => 10],
            'characteristic' => ['signs_of_distress' => 'none'],
            'rating' => ['consequence_to_life' => 'category-2'],
            'engineer_inspection' => now()->addYear(),
            'maintenance_inspection' => now()->addMonths(6),
        ]
    );
}

Slope::query()->updateOrCreate(
    ['slug' => 'sit-unranked'],
    [
        'slope_name' => 'SIT-UNRANKED',
        'location' => 'KM UNRANKED',
        'sta1' => '1+000',
        'sta2' => '1+050',
        'latitude' => '-7.2',
        'longtitude' => '110.5',
        'side_of_road' => 'A',
        'slope_type' => 'cut-type',
        'ranking' => null,
        'geometry' => ['feature_height' => 8],
        'characteristic' => [],
        'rating' => [],
    ]
);

Slope::query()->updateOrCreate(
    ['slug' => 'sit-nocoord'],
    [
        'slope_name' => 'SIT-NOCOORD',
        'location' => 'KM NOCOORD',
        'sta1' => '2+000',
        'sta2' => '2+050',
        'latitude' => null,
        'longtitude' => null,
        'side_of_road' => 'B',
        'slope_type' => 'cut-type',
        'ranking' => ['IS' => 1, 'CS' => 50, 'TS' => 50, 'RS' => 3.15],
        'geometry' => ['feature_height' => 8],
        'characteristic' => [],
        'rating' => ['consequence_to_life' => 'category-2'],
    ]
);

Inspection::query()->whereIn('approval_status', Inspection::OPEN_STATUSES)->delete();

echo "users+slopes ready\n";
