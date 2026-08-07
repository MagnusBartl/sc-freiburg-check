#!/usr/bin/env python3
"""Zeigt die letzten Bundesliga-Ergebnisse und den aktuellen Tabellenplatz von SC Freiburg."""

import sys
from datetime import datetime

import requests

LEAGUE = "bl1"
TEAM_NAME = "SC Freiburg"
API_BASE = "https://api.openligadb.de"


def get_table(season):
    resp = requests.get(f"{API_BASE}/getbltable/{LEAGUE}/{season}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_matches(season):
    resp = requests.get(f"{API_BASE}/getmatchdata/{LEAGUE}/{season}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def resolve_season():
    """Ermittelt die aktuelle Saison; faellt auf die Vorsaison zurueck, falls die neue noch nicht begonnen hat."""
    now = datetime.now()
    candidate = now.year if now.month >= 7 else now.year - 1
    table = get_table(candidate)
    if any(team["matches"] > 0 for team in table):
        return candidate, table
    previous = candidate - 1
    return previous, get_table(previous)


def print_table_position(table):
    for position, team in enumerate(table, start=1):
        if TEAM_NAME.lower() in team["teamName"].lower():
            print(f"\nTabellenplatz: {position}.")
            print(f"Punkte: {team['points']} ({team['matches']} Spiele)")
            print(f"Bilanz: {team['won']}S / {team['draw']}U / {team['lost']}N")
            print(f"Tore: {team['goals']}:{team['opponentGoals']} (Differenz: {team['goalDiff']:+d})")
            return
    print("SC Freiburg nicht in der Tabelle gefunden.")


def print_last_results(matches, count=5):
    played = [
        m for m in matches
        if m.get("matchIsFinished")
        and (TEAM_NAME.lower() in m["team1"]["teamName"].lower()
             or TEAM_NAME.lower() in m["team2"]["teamName"].lower())
    ]
    played.sort(key=lambda m: m["matchDateTimeUTC"])
    last = played[-count:]

    print(f"Letzte {len(last)} Ergebnisse:")
    for match in reversed(last):
        date = match["matchDateTime"][:10]
        team1 = match["team1"]["teamName"]
        team2 = match["team2"]["teamName"]
        final = next(
            (r for r in match["matchResults"] if r["resultTypeID"] == 2),
            match["matchResults"][-1] if match["matchResults"] else None,
        )
        score = f"{final['pointsTeam1']}:{final['pointsTeam2']}" if final else "?:?"
        print(f"  {date}  {team1} {score} {team2}")


def main():
    try:
        season, table = resolve_season()
        matches = get_matches(season)
    except requests.RequestException as exc:
        print(f"Fehler beim Abrufen der Daten: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"=== SC Freiburg – Bundesliga {season}/{season + 1 - 2000} ===\n")
    print_last_results(matches)
    print_table_position(table)


if __name__ == "__main__":
    main()
