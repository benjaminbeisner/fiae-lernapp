"""Erzeugt Übungsaufgaben aus Vorlagen (Rechenaufgaben) und Faktentabellen.

Jede Vorlage erzeugt mit festem Zufalls-Seed immer dieselben Varianten, damit Schlüssel
und Lernstand stabil bleiben. Varianten einer Vorlage teilen sich eine `gruppe`; die App
zeigt pro Sitzung höchstens eine Variante je Gruppe.
"""
