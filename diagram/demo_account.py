from django.utils.timezone import now
from datetime import timedelta as d
from diagram.models import Soldier, Activity, SoldierInfo, Subdivision, User, EverydayActivity
from activity_colors.models import ActivityColor


def delete_demo_data_from_deleted_guests():
    sldrs = Soldier.objects.filter(demo=True)
    actvts = Activity.objects.filter(demo=True)
    evrd_actvts = EverydayActivity.objects.filter(demo=True)
    actvts_clrs = ActivityColor.objects.filter(demo=True)
    sbdvs = Subdivision.objects.filter(demo=True)

    for objcs in [sldrs, actvts, evrd_actvts, actvts_clrs]:
        for obj in objcs:
            if User.objects.filter(subdivision=obj.subdivision).count() == 0:
                obj.delete()

    for obj in sbdvs:
        if User.objects.filter(subdivision=obj).count() == 0:
            obj.delete()

def create_demo_data(subdivision):
    today = now()

    # act_clrs = ActivityColor.objects.filter(subdivision=subdivision)
    # for act in act_clrs:
    #     act.demo = True
    #     act.save()

    soldier = Soldier.objects.create(subdivision=subdivision, rank='st. szer. spec.', first_name='Jan',
                                     last_name='Kowalski', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'starszy operator'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.value = 'Dariusz'
    info2.demo = True
    info2.save()
    info3 = SoldierInfo.objects.get(soldier=soldier, name='kat. prawa jazdy')
    info3.value = 'B, C, E'
    info3.demo = True
    info3.save()
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='UR.WYP', start_date=today - d(days=5),
                            end_date=today + d(days=4), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='POLIG', start_date=today + d(days=8),
                            end_date=today + d(days=20), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='kpr.', first_name='Michał', last_name='Zdun', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'operator'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.demo = True
    info2.value = 'Maciej'
    info2.save()
    info3 = SoldierInfo.objects.get(soldier=soldier, name='kat. prawa jazdy')
    info3.demo = True
    info3.value = 'B'
    info3.save()
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='L4', start_date=today - d(days=15),
                            end_date=today + d(days=10), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='plut.', first_name='Robert', last_name='Biały', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'dowódca obsługi'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.value = 'Jerzy'
    info2.demo = True
    info2.save()
    info3 = SoldierInfo.objects.get(soldier=soldier, name='PESEL')
    info3.value = '85030311123'
    info3.demo = True
    info3.save()
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='DYŻUR', start_date=today + d(days=3),
                            end_date=today + d(days=18), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='sierż.', first_name='Albert', last_name='Czerwony', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'specjalista'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.value = 'Rafał'
    info2.demo = True
    info2.save()
    info3 = SoldierInfo.objects.get(soldier=soldier, name='PESEL')
    info3.value = '82010112312'
    info3.demo = True
    info3.save()
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='KURS', start_date=today - d(days=20),
                            end_date=today + d(days=4), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='SŁ.PDF', start_date=today + d(days=8),
                            end_date=today + d(days=8), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='PO SŁ.', start_date=today + d(days=9),
                            end_date=today + d(days=9), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='mł. chor.', first_name='Rafał', last_name='Niebieski', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'dowódca plutonu'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='nr leg. sł.')
    info2.demo = True
    info2.value = 'XX 010203'
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='WOLNE', start_date=today - d(days=10),
                            end_date=today - d(days=1), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='HDK', start_date=today + d(days=3),
                            end_date=today + d(days=4), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='st. chor. sztab.', first_name='Krzysztof', last_name='Żółty', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'starszy technik stacji'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='nr leg. sł.')
    info2.demo = True
    info2.value = 'YY 010203'
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='INNE', start_date=today,
                            end_date=today, description='przegląd pojazdu URAL o numerze rej. UC 00001', demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='PS', start_date=today + d(days=6),
                            end_date=today + d(days=22), demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='ppor.', first_name='Adam', last_name='Fioletowy', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'dowódca plutonu'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.value = 'Eryk'
    info2.demo = True
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='SŁ.OF', start_date=today + d(days=1),
                            end_date=today + d(days=1), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='PO SŁ.', start_date=today + d(days=2),
                            end_date=today + d(days=2), demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='UR.OJC', start_date=today + d(days=5),
                            end_date=today + d(days=15), description='w związku z narodzinami syna', demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='kpt.', first_name='Dawid', last_name='Pomarańczowy', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.demo = True
    info1.value = 'dowódca baterii'
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.demo = True
    info2.value = 'Zdzisław'
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='UR.OK', start_date=today - d(days=15),
                            end_date=today - d(days=10), demo=True)


    soldier = Soldier.objects.create(subdivision=subdivision, rank='mjr', first_name='Maciej', last_name='Czarny', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.value = 'dowódca zespołu'
    info1.demo = True
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.value = 'Błażej'
    info2.demo = True
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='DYŻUR', start_date=today - d(days=5),
                            end_date=today + d(days=10), description='zastępuje kpt. Pomarańczowy', demo=True)

    soldier = Soldier.objects.create(subdivision=subdivision, rank='st. kpr.', first_name='Wojciech', last_name='Zielony', demo=True)
    info1 = SoldierInfo.objects.get(soldier=soldier, name='stanowisko')
    info1.demo = True
    info1.value = 'kierowca'
    info1.save()
    info2 = SoldierInfo.objects.get(soldier=soldier, name='imię ojca')
    info2.demo = True
    info2.value = 'Geralt'
    info2.save()

    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='PA GAR', start_date=today,
                            end_date=today, demo=True)
    Activity.objects.create(subdivision=subdivision, soldier=soldier, name='PO SŁ.', start_date=today + d(days=1),
                            end_date=today + d(days=1), demo=True)
