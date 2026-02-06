const { contextBridge, ipcRenderer } = require('electron');

// Exposer les APIs sécurisées au processus de rendu
contextBridge.exposeInMainWorld('electronAPI', {
    // ================================
    // INFORMATIONS DE L'APPLICATION
    // ================================
    
    /**
     * Obtenir les informations de l'application
     */
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),
    
    /**
     * Obtenir la version d'Electron et Node.js
     */
    getVersions: () => ({
        node: process.versions.node,
        chrome: process.versions.chrome,
        electron: process.versions.electron,
        platform: process.platform,
        arch: process.arch
    }),
    
    // ================================
    // CONTRÔLE DE DJANGO
    // ================================
    
    /**
     * Redémarrer le serveur Django
     */
    restartDjango: () => ipcRenderer.invoke('restart-django'),
    
    /**
     * Vérifier le statut de Django
     */
    isDjangoRunning: async () => {
        const appInfo = await ipcRenderer.invoke('get-app-info');
        return appInfo.djangoRunning;
    },
    
    /**
     * Obtenir l'URL de Django
     */
    getDjangoUrl: async () => {
        const appInfo = await ipcRenderer.invoke('get-app-info');
        return appInfo.djangoUrl;
    },
    
    // ================================
    // GESTION DES ÉVÉNEMENTS
    // ================================
    
    /**
     * Écouter les mises à jour de statut
     */
    onStatusUpdate: (callback) => {
        ipcRenderer.on('status-update', (event, message) => {
            callback(message);
        });
    },
    
    /**
     * Écouter les erreurs
     */
    onError: (callback) => {
        ipcRenderer.on('error-message', (event, error) => {
            callback(error);
        });
    },
    
    /**
     * Supprimer tous les listeners
     */
    removeAllListeners: () => {
        ipcRenderer.removeAllListeners('status-update');
        ipcRenderer.removeAllListeners('error-message');
    },
    
    // ================================
    // UTILITAIRES SYSTÈME
    // ================================
    
    /**
     * Informations sur la plateforme
     */
    platform: process.platform,
    
    /**
     * Vérifier si on est en mode développement
     */
    isDev: () => process.env.NODE_ENV === 'development' || process.argv.includes('--dev'),
    
    /**
     * Obtenir les arguments de ligne de commande
     */
    getArgs: () => process.argv,
    
    // ================================
    // FONCTIONS UTILITAIRES POUR L'UI
    // ================================
    
    /**
     * Tester la connexion à Django
     */
    testDjangoConnection: async () => {
        try {
            const appInfo = await ipcRenderer.invoke('get-app-info');
            const response = await fetch(appInfo.djangoUrl, { 
                method: 'HEAD',
                mode: 'no-cors'
            });
            return true;
        } catch (error) {
            return false;
        }
    },
    
    /**
     * Attendre que Django soit prêt
     */
    waitForDjango: (callback, timeout = 30000) => {
        const startTime = Date.now();
        const checkInterval = 1000; // Vérifier toutes les secondes
        
        const check = async () => {
            const isReady = await electronAPI.testDjangoConnection();
            
            if (isReady) {
                callback(true);
                return;
            }
            
            if (Date.now() - startTime > timeout) {
                callback(false);
                return;
            }
            
            setTimeout(check, checkInterval);
        };
        
        check();
    },
    
    // ================================
    // GESTION DES LOGS (si nécessaire)
    // ================================
    
    /**
     * Obtenir les logs de l'application
     */
    getLogs: () => ipcRenderer.invoke('get-logs'),
    
    /**
     * Envoyer un log au processus principal
     */
    log: (level, message) => {
        ipcRenderer.send('renderer-log', { level, message, timestamp: new Date().toISOString() });
    },
    
    // ================================
    // FONCTIONS DE DEBUG
    // ================================
    
    /**
     * Activer/désactiver les outils de développement
     */
    toggleDevTools: () => {
        ipcRenderer.send('toggle-dev-tools');
    },
    
    /**
     * Recharger la page
     */
    reload: () => {
        ipcRenderer.send('reload-page');
    }
});

// ================================
// FONCTIONS GLOBALES POUR LA CONSOLE
// ================================

// Exposer quelques fonctions utiles dans la console pour le debug
if (process.argv.includes('--dev')) {
    contextBridge.exposeInMainWorld('damaDebug', {
        getAppInfo: () => ipcRenderer.invoke('get-app-info'),
        restartDjango: () => ipcRenderer.invoke('restart-django'),
        testConnection: () => electronAPI.testDjangoConnection(),
        platform: process.platform,
        versions: process.versions
    });
}

// ================================
// INITIALISATION
// ================================

// Log de démarrage
console.log('🔒 Preload script chargé - APIs sécurisées exposées');

// Vérifier que contextBridge fonctionne
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        console.log('🌐 DOM chargé, APIs Electron disponibles');
        
        // Test rapide des APIs
        if (window.electronAPI) {
            console.log('✅ electronAPI disponible');
            
            // Obtenir les infos de l'app
            window.electronAPI.getAppInfo().then(info => {
                console.log('📱 Info app:', info);
            }).catch(err => {
                console.error('❌ Erreur info app:', err);
            });
        } else {
            console.error('❌ electronAPI non disponible');
        }
    });
}

// ================================
// GESTION DES ERREURS
// ================================

// Capturer les erreurs du renderer et les envoyer au main process
window.addEventListener('error', (event) => {
    ipcRenderer.send('renderer-error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error?.stack || event.error?.toString(),
        timestamp: new Date().toISOString()
    });
});

// Capturer les promises rejetées non gérées
window.addEventListener('unhandledrejection', (event) => {
    ipcRenderer.send('renderer-error', {
        message: 'Unhandled Promise Rejection',
        error: event.reason?.stack || event.reason?.toString(),
        timestamp: new Date().toISOString()
    });
});

// ================================
// SÉCURITÉ
// ================================

// Empêcher l'accès direct au module Node.js
delete window.require;
delete window.exports;
delete window.module;

// Bloquer eval() pour plus de sécurité
window.eval = function() {
    throw new Error('eval() est désactivé pour des raisons de sécurité');
};

console.log('🛡️ Sécurité renforcée activée');
