# -*- coding: utf-8 -*-

import re,os, sys
import xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs

my_addon                = xbmcaddon.Addon()
my_addon_name           = my_addon.getAddonInfo('name')



#------------------------------#
#--       Clear Cache        --#
#------------------------------#

def clearCache():
    print '###'+my_addon_name+' - CLEARING CACHE FILES###'
    #- Windows -#
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'cache')
    if os.path.exists(xbmc_cache_path)==True:
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Usuwanie plików tymczasowych", "Znalezionych plików: " + str(file_count), "Czy chcesz je usunąć?"):
                    for f in files:
                        try:
                            if not f == 'commoncache.db':
                                os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
            else:
                pass
    #- Android -#
    xbmc_cache_path = os.path.join(xbmc.translatePath('special://home'), 'temp')
    if os.path.exists(xbmc_cache_path)==True:
        for root, dirs, files in os.walk(xbmc_cache_path):
            file_count = 0
            file_count += len(files)
            if file_count > 0:
                dialog = xbmcgui.Dialog()
                if dialog.yesno("Usuwanie plików tymczasowych", "Znalezionych plików: " + str(file_count), "Czy chcesz je usunąć?"):
                    for f in files:
                        try:
                            if not f == 'commoncache.db':
                                os.unlink(os.path.join(root, f))
                        except:
                            pass
                    for d in dirs:
                        try:
                            shutil.rmtree(os.path.join(root, d))
                        except:
                            pass
            else:
                pass
    if xbmc.getCondVisibility('system.platform.ATV2'):
        atv2_cache_a = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'Other')

        for root, dirs, files in os.walk(atv2_cache_a):
            file_count = 0
            file_count += len(files)

            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete ATV2 Cache Files", str(file_count) + " files found in 'Other'", "Do you want to delete them?"):

                    for f in files:
                        if not f == 'commoncache.db':
                            os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))

            else:
                pass
        atv2_cache_b = os.path.join('/private/var/mobile/Library/Caches/AppleTV/Video/', 'LocalAndRental')

        for root, dirs, files in os.walk(atv2_cache_b):
            file_count = 0
            file_count += len(files)

            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Delete ATV2 Cache Files", str(file_count) + " files found in 'LocalAndRental'", "Do you want to delete them?"):

                    for f in files:
                        if not f == 'commoncache.db':
                            os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))

            else:
                pass
              # Set path to Cydia Archives cache files



    dialog = xbmcgui.Dialog()
    dialog.ok(my_addon_name, "Czyszczenie zakończone")

def eraseLogs():
    print '###'+my_addon_name+' - DELETING CRASH LOGS###'
    dialog = xbmcgui.Dialog()
    if dialog.yesno(my_addon_name, "Czy chcesz usunąć logi awarii?", "Log systemowy nie zostanie usunięty"):
        path=logLocation()
        for infile in glob.glob(os.path.join(path, 'xbmc_crashlog*.*')):
             File=infile
             print infile
             os.remove(infile)
             dialog = xbmcgui.Dialog()
             dialog.ok(my_addon_name, "Zrestartuj KODI !!")
    else:
            pass

def logLocation():
    versionNumber = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
    if versionNumber < 12:
        if xbmc.getCondVisibility('system.platform.osx'):
            if xbmc.getCondVisibility('system.platform.atv2'):
                log_path = '/var/mobile/Library/Preferences'
            else:
                log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
        elif xbmc.getCondVisibility('system.platform.ios'):
            log_path = '/var/mobile/Library/Preferences'
        elif xbmc.getCondVisibility('system.platform.windows'):
            log_path = xbmc.translatePath('special://home')
        elif xbmc.getCondVisibility('system.platform.linux'):
            log_path = xbmc.translatePath('special://home/temp')
        else:
            log_path = xbmc.translatePath('special://logpath')
    elif versionNumber > 11:
        log_path = xbmc.translatePath('special://logpath')
    return log_path

def deletePackages():
    print '###'+my_addon_name+' - DELETING PACKAGES###'
    packages_cache_path = xbmc.translatePath(os.path.join('special://home/addons/packages', ''))
    try:
        for root, dirs, files in os.walk(packages_cache_path):
            file_count = 0
            file_count += len(files)

        # Count files and give option to delete
            if file_count > 0:

                dialog = xbmcgui.Dialog()
                if dialog.yesno("Usuwanie plików archiwalnych", "Znalezionych plików: " + str(file_count), "Czy chcesz je usunąć?"):

                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                    dialog = xbmcgui.Dialog()
                    dialog.ok(my_addon_name, "       Usuwanie plików zakończone ")
                else:
                        pass
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok(my_addon_name, "       Nie znaleziono plików archiwalnych")
    except:
        dialog = xbmcgui.Dialog()
        dialog.ok(my_addon_name, "Wystąpił błąd podczas usuwania")
