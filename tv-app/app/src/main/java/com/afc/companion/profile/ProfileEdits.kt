package com.afc.companion.profile

/** Pure profile edit operations behind the Profile/Settings screen buttons, so each edit is host-testable. */

enum class SelectionKind { Leagues, Teams, Players, FavoriteTeams }

/** Adds the trimmed value when absent, removes it when present; blank input changes nothing. */
fun FantasySelections.toggled(kind: SelectionKind, raw: String): FantasySelections {
    val value = raw.trim()
    if (value.isEmpty()) return this
    fun Set<String>.toggle() = if (value in this) this - value else this + value
    return when (kind) {
        SelectionKind.Leagues -> copy(leagues = leagues.toggle())
        SelectionKind.Teams -> copy(teams = teams.toggle())
        SelectionKind.Players -> copy(players = players.toggle())
        SelectionKind.FavoriteTeams -> copy(favoriteTeams = favoriteTeams.toggle())
    }
}

fun FantasySelections.values(kind: SelectionKind): Set<String> = when (kind) {
    SelectionKind.Leagues -> leagues
    SelectionKind.Teams -> teams
    SelectionKind.Players -> players
    SelectionKind.FavoriteTeams -> favoriteTeams
}

fun Set<AlertType>.toggled(type: AlertType): Set<AlertType> = if (type in this) this - type else this + type

/** A team/league pair only exists when both names are present. */
fun teamLeagueOf(league: String, team: String): TeamLeague? {
    val l = league.trim()
    val t = team.trim()
    return if (l.isEmpty() || t.isEmpty()) null else TeamLeague(l, t)
}

fun List<TimeWindow>.removeWindowAt(index: Int): List<TimeWindow> =
    if (index !in indices) this else filterIndexed { i, _ -> i != index }

/** Moves one window edge by [deltaMinutes], wrapping around the local day. */
fun List<TimeWindow>.adjustWindow(index: Int, adjustStart: Boolean, deltaMinutes: Int): List<TimeWindow> =
    mapIndexed { i, w ->
        if (i != index) w
        else if (adjustStart) w.copy(startMinute = (w.startMinute + deltaMinutes).mod(1440))
        else w.copy(endMinute = (w.endMinute + deltaMinutes).mod(1440))
    }

fun ProviderPreference.addProvider(raw: String): ProviderPreference {
    val value = raw.trim()
    return if (value.isEmpty() || value in order) this else copy(order = order + value)
}

fun ProviderPreference.removeProvider(provider: String): ProviderPreference =
    copy(order = order - provider, confirmedAccess = confirmedAccess - provider, appOverrides = appOverrides - provider)

fun ProviderPreference.moveProviderUp(index: Int): ProviderPreference {
    if (index !in 1..order.lastIndex) return this
    val reordered = order.toMutableList()
    reordered[index - 1] = order[index]
    reordered[index] = order[index - 1]
    return copy(order = reordered)
}

fun ProviderPreference.toggleConfirmedAccess(provider: String): ProviderPreference =
    copy(confirmedAccess = if (provider in confirmedAccess) confirmedAccess - provider else confirmedAccess + provider)

/** Cycles a detected-app override: automatic -> installed -> not installed -> automatic. */
fun ProviderPreference.cycleAppOverride(packageName: String): ProviderPreference {
    val name = packageName.trim()
    if (name.isEmpty()) return this
    val overrides = when (appOverrides[name]) {
        null -> appOverrides + (name to true)
        true -> appOverrides + (name to false)
        false -> appOverrides - name
    }
    return copy(appOverrides = overrides)
}

fun ProviderPreference.withLocalMarket(raw: String?): ProviderPreference =
    copy(localMarket = raw?.trim()?.takeIf { it.isNotEmpty() })
