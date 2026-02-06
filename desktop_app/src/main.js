const { app, BrowserWindow, Menu, dialog, shell, ipcMain } = require('electron');
const { autoUpdater } = require('electron-updater');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const log = require('electron-log');

// Configuration de l'application
const APP_CONFIG = {
    name: 'WELTO',
    version: '1.0.0',
    djangoPort: 8000,
    djangoHost: '127.0.0.1',
    windowWidth: 1400,
    windowHeight: 900,
    minWidth: 1000,
    minHeight: 700
};

// Variables globales
let mainWindow;
let djangoProcess;
let isDjangoRunning = false;
let startupAttempts = 0;
const maxStartupAttempts = 5; // Augmenté de 3 à 5
let healthCheckInterval;
let lastConnectionTime = Date.now();

// Configuration userData (Windows: %APPDATA%\WELTO)
const userDataPath = app.getPath('userData');
const dataDir = path.join(userDataPath, 'data');
const backupDir = path.join(userDataPath, 'backups');

// Configuration des logs
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Configuration d'electron-updater
autoUpdater.logger = log;
autoUpdater.autoDownload = false; // Demander confirmation avant téléchargement

/**
 * Initialiser les dossiers userData
 */
function initializeUserDataDirectories() {
    log.info(`UserData path: ${userDataPath}`);
    
    // Créer les dossiers nécessaires
    [dataDir, backupDir].forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
            log.info(`Dossier créé: ${dir}`);
        }
    });
    
    // Passer le chemin userData à Django via variable d'environnement
    process.env.WELTO_USER_DATA = userDataPath;
    log.info('Variable WELTO_USER_DATA configurée pour Django');
}

/**
 * Migration automatique de l'ancienne base de données
 */
function migrateDatabaseIfNeeded() {
    const oldDbPath = path.join(process.resourcesPath, 'db.sqlite3');
    const newDbPath = path.join(dataDir, 'db.sqlite3');
    
    // Si l'ancienne BD existe et la nouvelle n'existe pas, migrer
    if (fs.existsSync(oldDbPath) && !fs.existsSync(newDbPath)) {
        log.info('Migration de la base de données vers userData...');
        log.info(`Source: ${oldDbPath}`);
        log.info(`Destination: ${newDbPath}`);
        
        try {
            // Copier la base de données
            fs.copyFileSync(oldDbPath, newDbPath);
            
            // Copier les fichiers WAL si ils existent
            const oldWalPath = oldDbPath + '-wal';
            const oldShmPath = oldDbPath + '-shm';
            const newWalPath = newDbPath + '-wal';
            const newShmPath = newDbPath + '-shm';
            
            if (fs.existsSync(oldWalPath)) {
                fs.copyFileSync(oldWalPath, newWalPath);
            }
            if (fs.existsSync(oldShmPath)) {
                fs.copyFileSync(oldShmPath, newShmPath);
            }
            
            log.info('Migration terminée avec succès');
            
            // Créer un backup de la migration
            backupDatabase('migration_initiale');
            
        } catch (error) {
            log.error('Erreur lors de la migration:', error);
            dialog.showErrorBox(
                'Erreur de Migration',
                `Impossible de migrer la base de données:\n${error.message}\n\n` +
                `L'application va démarrer avec une nouvelle base vide.`
            );
        }
    }
}

/**
 * Créer un backup de la base de données
 */
function backupDatabase(suffix = null) {
    const dbPath = path.join(dataDir, 'db.sqlite3');
    
    if (!fs.existsSync(dbPath)) {
        log.warn('Pas de base de données à sauvegarder');
        return false;
    }
    
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const backupName = suffix 
            ? `db_${suffix}_${timestamp}.sqlite3`
            : `db_${timestamp}.sqlite3`;
        const backupPath = path.join(backupDir, backupName);
        
        fs.copyFileSync(dbPath, backupPath);
        log.info(`Backup créé: ${backupPath}`);
        
        // Nettoyer les anciens backups (garder seulement les 5 derniers)
        cleanOldBackups();
        
        return true;
    } catch (error) {
        log.error('Erreur lors du backup:', error);
        return false;
    }
}

/**
 * Nettoyer les anciens backups (garder seulement les 5 derniers)
 */
function cleanOldBackups() {
    try {
        const backups = fs.readdirSync(backupDir)
            .filter(file => file.startsWith('db_') && file.endsWith('.sqlite3'))
            .map(file => ({
                name: file,
                path: path.join(backupDir, file),
                time: fs.statSync(path.join(backupDir, file)).mtime.getTime()
            }))
            .sort((a, b) => b.time - a.time); // Trier par date décroissante
        
        // Supprimer les backups au-delà des 5 derniers
        if (backups.length > 5) {
            backups.slice(5).forEach(backup => {
                fs.unlinkSync(backup.path);
                log.info(`Ancien backup supprimé: ${backup.name}`);
            });
        }
    } catch (error) {
        log.error('Erreur lors du nettoyage des backups:', error);
    }
}

// ================================
// SYSTEME DE MISE A JOUR AUTOMATIQUE
// ================================

/**
 * Vérifier les mises à jour disponibles
 */
function checkForUpdates() {
    log.info('Vérification des mises à jour...');
    autoUpdater.checkForUpdates();
}

// Événement: Vérification des mises à jour en cours
autoUpdater.on('checking-for-update', () => {
    log.info('Vérification des mises à jour en cours...');
});

// Événement: Mise à jour disponible
autoUpdater.on('update-available', (info) => {
    log.info(`Mise à jour disponible: v${info.version}`);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Mise à jour disponible',
            message: `Une nouvelle version ${info.version} est disponible.`,
            detail: 'Voulez-vous télécharger et installer la mise à jour maintenant?\n\n' +
                   'Vos données seront automatiquement sauvegardées avant la mise à jour.',
            buttons: ['Oui, mettre à jour', 'Plus tard'],
            defaultId: 0,
            cancelId: 1
        }).then((result) => {
            if (result.response === 0) {
                log.info('Téléchargement de la mise à jour...');
                autoUpdater.downloadUpdate();
            }
        });
    }
});

// Événement: Pas de mise à jour disponible
autoUpdater.on('update-not-available', (info) => {
    log.info('Aucune mise à jour disponible');
});

// Événement: Erreur lors de la vérification
autoUpdater.on('error', (err) => {
    log.error('Erreur lors de la mise à jour:', err);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
        // Ne pas afficher de message d'erreur intrusif, juste logger
        log.warn('La vérification des mises à jour a échoué (connexion Internet?)');
    }
});

// Événement: Progression du téléchargement
autoUpdater.on('download-progress', (progressObj) => {
    const percent = Math.round(progressObj.percent);
    log.info(`Téléchargement: ${percent}%`);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.setTitle(`WELTO - Téléchargement: ${percent}%`);
    }
});

// Événement: Mise à jour téléchargée
autoUpdater.on('update-downloaded', (info) => {
    log.info(`Mise à jour v${info.version} téléchargée`);
    
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.setTitle('WELTO');
        
        dialog.showMessageBox(mainWindow, {
            type: 'info',
            title: 'Mise à jour prête',
            message: 'La mise à jour a été téléchargée avec succès.',
            detail: 'L\'application va redémarrer pour installer la mise à jour.\n' +
                   'Vos données sont en sécurité dans votre dossier utilisateur.',
            buttons: ['Redémarrer maintenant', 'Redémarrer plus tard'],
            defaultId: 0,
            cancelId: 1
        }).then((result) => {
            if (result.response === 0) {
                // Créer un backup avant la mise à jour
                log.info('Création d\'un backup avant la mise à jour...');
                backupDatabase('avant_maj');
                
                // Quitter et installer
                log.info('Installation de la mise à jour...');
                autoUpdater.quitAndInstall(false, true);
            }
        });
    }
});

/**
 * Créer la fenêtre principale de l'application
 */
function createWindow() {
    log.info('Création de la fenêtre principale...');
    
    mainWindow = new BrowserWindow({
        width: APP_CONFIG.windowWidth,
        height: APP_CONFIG.windowHeight,
        minWidth: APP_CONFIG.minWidth,
        minHeight: APP_CONFIG.minHeight,
        icon: getAppIcon(),
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js'),
            webSecurity: true
        },
        show: false, // Ne pas afficher immédiatement
        titleBarStyle: 'default',
        autoHideMenuBar: false,
        backgroundColor: '#667eea' // Couleur de fond pendant le chargement
    });

    // Charger l'interface de chargement
    mainWindow.loadFile(path.join(__dirname, 'loading.html'));

    // Afficher la fenêtre quand elle est prête
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        log.info('Fenêtre principale affichée');
        
        // Démarrer Django après un court délai
        setTimeout(() => {
            startDjangoServer();
        }, 2000); // Augmenté pour laisser le temps à l'interface de se charger
    });

    // Gestion des événements de fenêtre
    mainWindow.on('closed', () => {
        log.info('Fenêtre principale fermée');
        mainWindow = null;
    });

    // Empêcher la navigation vers des sites externes
    mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);
        
        if (parsedUrl.origin !== `http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}`) {
            event.preventDefault();
            log.warn(`Navigation bloquée vers: ${navigationUrl}`);
        }
    });

    // Ouvrir les liens externes dans le navigateur
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Mode développement
    if (process.argv.includes('--dev')) {
        mainWindow.webContents.openDevTools();
        log.info('Mode développement activé');
    }
}

/**
 * Obtenir le chemin de l'icône de l'application
 */
function getAppIcon() {
    // Priorité à logo.ico
    const logoPath = path.join(__dirname, '../assets/logo.ico');
    if (fs.existsSync(logoPath)) {
        return logoPath;
    }
    
    // Fallback vers icon.ico
    const iconPath = path.join(__dirname, '../assets/icon.ico');
    if (fs.existsSync(iconPath)) {
        return iconPath;
    }
    
    return null; // Utiliser l'icône par défaut d'Electron
}

/**
 * Vérifier si le port 8000 est libre
 */
function checkPortAvailable(port, host = '127.0.0.1') {
    return new Promise((resolve) => {
        const net = require('net');
        const tester = net.createServer()
            .once('error', () => resolve(false))
            .once('listening', () => {
                tester.once('close', () => resolve(true)).close();
            })
            .listen(port, host);
    });
}

/**
 * Démarrer le serveur Django (SIMPLIFIÉ POUR ÉVITER LES BOUCLES)
 */
function startDjangoServer() {
    // Protection contre les lancements multiples
    if (isDjangoRunning || djangoProcess) {
        log.warn('Django est déjà en cours d\'exécution ou en démarrage');
        return;
    }

    startupAttempts++;
    log.info(`Tentative de démarrage Django #${startupAttempts}...`);
    
    updateLoadingStatus('Démarrage du serveur Django...');

    const pythonPath = findPythonPath();
    
    if (!pythonPath) {
        showError('Python Introuvable', 
            'Python n\'a pas été trouvé sur ce système.\nVeuillez installer Python 3.8+ et réessayer.');
        return;
    }

    log.info(`Utilisation de Python: ${pythonPath}`);

    // En mode production, pas besoin de vérifier djangoPath car l'exécutable est autonome
    if (!app.isPackaged) {
        const djangoPath = getDjangoPath();
        if (!djangoPath) {
            showError('Django Introuvable', 
                'Le dossier backend Django est introuvable.\nVeuillez vérifier l\'installation.');
            return;
        }
        log.info(`Dossier Django: ${djangoPath}`);
    }

    // Démarrer le processus Django - Mode adapté selon l'environnement
    if (app.isPackaged) {
        // En production : utiliser l'exécutable bundlé onedir
        // IMPORTANT: lancer depuis le dossier resources (où sont les données Django)
        djangoProcess = spawn(pythonPath, [], {
            cwd: process.resourcesPath,  // Lancer depuis resources (où est db.sqlite3)
            env: {
                ...process.env,
            }
        });
        log.info(`Mode production - Lancement exécutable Django onedir depuis: ${process.resourcesPath}`);
    } else {
        // En développement : utiliser Welto.py avec Python
        const djangoPath = getDjangoPath(); // Récupérer djangoPath seulement pour le mode développement
        djangoProcess = spawn(pythonPath, ['Welto.py'], {
            cwd: djangoPath,
            env: {
                ...process.env,
                PYTHONPATH: djangoPath,
                DJANGO_SETTINGS_MODULE: 'blog_pos.settings'
            }
        });
        log.info('Mode développement - Lancement Welto.py avec Python');
    }

    // Gestion des sorties
    djangoProcess.stdout.on('data', (data) => {
        const output = data.toString();
        log.info(`Django stdout: ${output.trim()}`);
        
        // Détecter quand Django est complètement prêt (optimisé avec pré-chargement)
        if (output.includes('[DAMA] Demarrage du serveur Django (Uvicorn)') ||
            output.includes('Uvicorn running on') ||
            output.includes('Application startup complete') ||
            output.includes('Django ASGI ultra-optimisé - PRÊT') ||
            output.includes('Tables principales pré-chargées') ||
            output.includes('Started server process')) {
            
            updateLoadingStatus('Optimisations chargées, connexion...');
            
            // Avec les optimisations WAL + pré-chargement, encore plus rapide
            setTimeout(() => {
                testAndLoadDjango();
            }, 800); // Réduit de 1500ms à 800ms grâce aux optimisations
        }
    });

    djangoProcess.stderr.on('data', (data) => {
        const error = data.toString();
        log.error(`Django stderr: ${error.trim()}`);
        
        // Ne pas traiter les warnings comme des erreurs fatales
        if (!error.toLowerCase().includes('warning')) {
            updateLoadingStatus('Erreur de démarrage Django...');
        }
    });

    djangoProcess.on('close', (code) => {
        log.info(`Processus Django fermé avec le code ${code}`);
        isDjangoRunning = false;
        djangoProcess = null; // IMPORTANT: Reset la variable
        
        // Redémarrage automatique SEULEMENT si c'est une fermeture inattendue
        if (mainWindow && !mainWindow.isDestroyed() && code !== 0) {
            if (startupAttempts < maxStartupAttempts) {
                log.warn(`Redémarrage automatique dans 3 secondes... (tentative ${startupAttempts}/${maxStartupAttempts})`);
                updateLoadingStatus(`Redémarrage serveur (${startupAttempts}/${maxStartupAttempts})...`);
                
                setTimeout(() => {
                    startDjangoServer();
                }, 3000); // Augmenté pour éviter les conflits
            } else {
                log.error('Trop de tentatives de redémarrage - abandon');
                showError('Serveur Instable', 
                    `Le serveur Django s'arrête de manière répétée.\n` +
                    `Code d'erreur: ${code}\n` +
                    `Tentatives échouées: ${startupAttempts}\n\n` +
                    `Essayez de redémarrer l'application complètement.`);
            }
        } else if (code === 0) {
            log.info('Django s\'est arrêté normalement');
        }
    });

    djangoProcess.on('error', (error) => {
        log.error('Erreur de démarrage Django:', error);
        isDjangoRunning = false;
        
        updateLoadingStatus('Erreur de démarrage...');
        showError('Erreur de Démarrage', 
            `Impossible de démarrer Django:\n${error.message}\n\n` +
            `Vérifiez que Python est correctement installé.`);
    });
}

/**
 * Tester la connexion Django puis charger l'application
 */
function testAndLoadDjango(retryCount = 0) {
    const maxRetries = 5;
    const djangoUrl = `http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}`;
    
    // Tester la connexion avec fetch
    fetch(djangoUrl, { method: 'HEAD' })
        .then(response => {
            if (response.ok) {
                isDjangoRunning = true;
                loadDjangoApp();
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        })
        .catch(error => {
            log.warn(`Test de connexion échoué (tentative ${retryCount + 1}/${maxRetries}): ${error.message}`);
            
            if (retryCount < maxRetries) {
                updateLoadingStatus(`Test de connexion... (${retryCount + 1}/${maxRetries})`);
                setTimeout(() => {
                    testAndLoadDjango(retryCount + 1);
                }, 2000);
            } else {
                log.error('Impossible de se connecter à Django après plusieurs tentatives');
                updateLoadingStatus('Erreur de connexion...');
                showError('Erreur de Connexion', 
                    `Impossible de se connecter au serveur Django après ${maxRetries} tentatives.\n\n` +
                    `Vérifiez que Django démarre correctement.`);
            }
        });
}

/**
 * Charger l'application Django dans la fenêtre
 */
function loadDjangoApp() {
    if (!mainWindow) return;
    
    const djangoUrl = `http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}`;
    log.info(`Chargement de l'application Django: ${djangoUrl}`);
    
    updateLoadingStatus('Chargement de l\'interface...');
    
    mainWindow.loadURL(djangoUrl).then(() => {
        log.info('Application Django chargée avec succès');
        lastConnectionTime = Date.now();
        
        // Démarrer la surveillance de santé
        startHealthCheck();
        
    }).catch((error) => {
        log.error('Erreur de chargement de l\'application:', error);
        updateLoadingStatus('Erreur de connexion...');
        
        setTimeout(() => {
            showError('Erreur de Connexion', 
                `Impossible de se connecter au serveur Django:\n${error.message}\n\n` +
                `Vérifiez que le serveur fonctionne correctement.`);
        }, 1000);
    });
}

/**
 * Surveillance de santé du serveur Django
 */
function startHealthCheck() {
    // Arrêter toute surveillance précédente
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
    }
    
    log.info('Démarrage de la surveillance de santé Django');
    
    healthCheckInterval = setInterval(() => {
        if (!isDjangoRunning) return;
        
        const djangoUrl = `http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}`;
        
        fetch(djangoUrl, { 
            method: 'HEAD',
            timeout: 5000 // 5 secondes de timeout
        })
        .then(response => {
            if (response.ok) {
                lastConnectionTime = Date.now();
            } else {
                log.warn(`Health check failed: HTTP ${response.status}`);
                handleConnectionLoss();
            }
        })
        .catch(error => {
            log.warn(`Health check failed: ${error.message}`);
            handleConnectionLoss();
        });
        
    }, 10000); // Vérification toutes les 10 secondes
}

/**
 * Gérer la perte de connexion
 */
function handleConnectionLoss() {
    const timeSinceLastConnection = Date.now() - lastConnectionTime;
    
    // Si plus de 30 secondes sans connexion valide
    if (timeSinceLastConnection > 30000) {
        log.error('Connexion Django perdue depuis plus de 30 secondes');
        
        if (healthCheckInterval) {
            clearInterval(healthCheckInterval);
            healthCheckInterval = null;
        }
        
        // Redémarrer Django automatiquement
        if (mainWindow && !mainWindow.isDestroyed()) {
            log.info('Tentative de reconnexion automatique...');
            
            // Afficher l'écran de chargement
            mainWindow.loadFile(path.join(__dirname, 'loading.html'));
            updateLoadingStatus('Reconnexion en cours...');
            
            // Redémarrer le serveur
            restartDjango();
        }
    }
}

/**
 * Trouver le chemin vers Python
 */
function findPythonPath() {
    // En production (app packagée), utiliser l'exécutable bundlé onedir
    if (app.isPackaged) {
        const bundledExe = path.join(process.resourcesPath, 'DAMA_Django_Server', 'DAMA_Django_Server.exe');
        log.info(`Mode production - Exécutable bundlé onedir: ${bundledExe}`);
        return bundledExe;
    }
    
    // En développement, utiliser Python classique
    const possiblePaths = [
        // Python dans l'environnement virtuel (priorité)
        path.join(__dirname, '../../dama_env/Scripts/python.exe'),
        // Python système
        'python',
        'python3',
        'py'
    ];

    for (const pythonPath of possiblePaths) {
        if (fs.existsSync(pythonPath)) {
            log.info(`Mode développement - Python trouvé: ${pythonPath}`);
            return pythonPath;
        }
    }

    // Fallback: essayer les commandes système
    return 'python';
}

/**
 * Obtenir le chemin vers le dossier Django
 */
function getDjangoPath() {
    const djangoPath = path.join(__dirname, '../../blog_pos');
    
    if (fs.existsSync(djangoPath)) {
        return djangoPath;
    }
    
    log.error(`Dossier Django introuvable: ${djangoPath}`);
    return null;
}

/**
 * Mettre à jour le statut de chargement
 */
function updateLoadingStatus(message) {
    if (mainWindow) {
        mainWindow.webContents.executeJavaScript(`
            if (document.getElementById('loading-status')) {
                document.getElementById('loading-status').textContent = '${message}';
            }
        `).catch(() => {
            // Ignore les erreurs si la page de chargement n'est plus active
        });
    }
}

/**
 * Afficher une boîte de dialogue d'erreur
 */
function showError(title, message) {
    log.error(`${title}: ${message}`);
    
    if (mainWindow) {
        dialog.showErrorBox(title, message);
    } else {
        console.error(`${title}: ${message}`);
    }
}

/**
 * Créer le menu de l'application
 */
function createMenu() {
    const template = [
        {
            label: 'Fichier',
            submenu: [
                {
                    label: 'Nouvelle Vente',
                    accelerator: 'CmdOrCtrl+N',
                    click: () => {
                        if (mainWindow && isDjangoRunning) {
                            mainWindow.loadURL(`http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}/`);
                        }
                    }
                },
                {
                    label: 'Tableau de Bord',
                    accelerator: 'CmdOrCtrl+D',
                    click: () => {
                        if (mainWindow && isDjangoRunning) {
                            mainWindow.loadURL(`http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}/old_dasboard`);
                        }
                    }
                },
                {
                    label: 'Liste des Commandes',
                    accelerator: 'CmdOrCtrl+L',
                    click: () => {
                        if (mainWindow && isDjangoRunning) {
                            mainWindow.loadURL(`http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}/order-list/`);
                        }
                    }
                },
                { type: 'separator' },
                {
                    label: 'Redémarrer Django',
                    click: () => {
                        restartDjango();
                    }
                },
                { type: 'separator' },
                {
                    label: 'Quitter',
                    accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
                    click: () => {
                        app.quit();
                    }
                }
            ]
        },
        {
            label: 'Édition',
            submenu: [
                { role: 'undo', label: 'Annuler' },
                { role: 'redo', label: 'Rétablir' },
                { type: 'separator' },
                { role: 'cut', label: 'Couper' },
                { role: 'copy', label: 'Copier' },
                { role: 'paste', label: 'Coller' },
                { role: 'selectall', label: 'Tout sélectionner' }
            ]
        },
        {
            label: 'Affichage',
            submenu: [
                { role: 'reload', label: 'Actualiser' },
                { role: 'forceReload', label: 'Actualiser (force)' },
                { role: 'toggleDevTools', label: 'Outils de développement' },
                { type: 'separator' },
                { role: 'resetZoom', label: 'Zoom normal' },
                { role: 'zoomIn', label: 'Zoom avant' },
                { role: 'zoomOut', label: 'Zoom arrière' },
                { type: 'separator' },
                { role: 'togglefullscreen', label: 'Plein écran' }
            ]
        },
        {
            label: 'Aide',
            submenu: [
                {
                    label: 'À propos de WELTO',
                    click: () => {
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'À propos de WELTO',
                            message: `WELTO v${APP_CONFIG.version}`,
                            detail: 'Welto est une solution de Point de Vente (POS) complète, développée par l\'ingénieur en intelligence artificielle Aliou Diallo. Elle intègre la gestion des commandes, des clients, des produits et de l\'inventaire, et permet de suivre vos ventes et vos stocks en temps réel, tout en offrant un tableau de bord analytique pour vos décisions stratégiques.\n\n' +
                                   'Nom commercial : WELTO\n' +
                                   'Version : 1.0.0\n\n' +
                                   'Développée par Aliou DIALLO\n' +
                                   'Ingenieur en intelligence artificielle\n\n' +
                                   'Copyright © 2024 GABITHEX TEAM\n' +
                                   'Contact: aliou@gabithex.fr\n' +
                                   '© 2025 WELTO. Tous droits réservés.'
                        });
                    }
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

/**
 * Redémarrer le serveur Django
 */
function restartDjango() {
    log.info('Redémarrage de Django demandé...');
    
    // Arrêter la surveillance de santé
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;
    }
    
    if (djangoProcess) {
        log.info('Arrêt du processus Django existant...');
        djangoProcess.kill('SIGTERM'); // Arrêt propre
        isDjangoRunning = false;
        
        // Attendre un peu pour l'arrêt propre
        setTimeout(() => {
            if (djangoProcess && !djangoProcess.killed) {
                log.warn('Force kill du processus Django...');
                djangoProcess.kill('SIGKILL');
            }
        }, 3000);
    }
    
    if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.loadFile(path.join(__dirname, 'loading.html'));
        updateLoadingStatus('Redémarrage du serveur...');
    }
    
    startupAttempts = 0; // Reset le compteur
    lastConnectionTime = Date.now(); // Reset le timer de connexion
    
    setTimeout(() => {
        startDjangoServer();
    }, 2000);
}

// ================================
// GESTIONNAIRES D'ÉVÉNEMENTS ELECTRON
// ================================

app.whenReady().then(() => {
    log.info(`Démarrage de ${APP_CONFIG.name} v${APP_CONFIG.version} - Solution POS par Aliou Diallo`);
    
    // Initialiser userData et migrer la base de données si nécessaire
    initializeUserDataDirectories();
    migrateDatabaseIfNeeded();
    
    createWindow();
    createMenu();
    
    // Vérifier les mises à jour après 30 secondes
    setTimeout(() => {
        if (!process.argv.includes('--dev')) {
            checkForUpdates();
        } else {
            log.info('Mode développement: vérification des mises à jour désactivée');
        }
    }, 30000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    log.info('Toutes les fenêtres fermées');
    
    // Nettoyer les intervalles
    if (healthCheckInterval) {
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;
    }
    
    // Arrêter Django proprement
    if (djangoProcess) {
        log.info('Arrêt du processus Django...');
        djangoProcess.kill('SIGTERM');
        
        // Force kill après 3 secondes si nécessaire
        setTimeout(() => {
            if (djangoProcess && !djangoProcess.killed) {
                djangoProcess.kill('SIGKILL');
            }
        }, 3000);
    }
    
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('before-quit', (event) => {
    log.info('Application en cours de fermeture...');
    
    // Arrêter Django proprement
    if (djangoProcess && isDjangoRunning) {
        log.info('Arrêt du serveur Django...');
        djangoProcess.kill();
        
        // Donner un peu de temps pour l'arrêt propre
        setTimeout(() => {
            app.quit();
        }, 1000);
        
        event.preventDefault(); // Empêcher la fermeture immédiate
    }
});

// Gestion des erreurs non capturées
process.on('uncaughtException', (error) => {
    log.error('Erreur non capturée:', error);
    showError('Erreur Critique', 
        `Une erreur critique s'est produite:\n${error.message}\n\n` +
        `L'application va se fermer.`);
    app.quit();
});

process.on('unhandledRejection', (reason, promise) => {
    log.error('Promise rejetée non gérée:', reason);
});

// ================================
// IPC POUR LA COMMUNICATION AVEC LE RENDERER
// ================================

ipcMain.handle('get-app-info', () => {
    return {
        name: APP_CONFIG.name,
        version: APP_CONFIG.version,
        djangoRunning: isDjangoRunning,
        djangoUrl: `http://${APP_CONFIG.djangoHost}:${APP_CONFIG.djangoPort}`
    };
});

ipcMain.handle('restart-django', () => {
    restartDjango();
    return true;
});

ipcMain.handle('get-logs', () => {
    // Retourner les logs récents si nécessaire
    return [];
});

log.info('Main process initialized');
