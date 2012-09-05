from twisted.python import log
import MySQLdb as mdb
import sys
from config import Config

class DbHelper:
  def __init__(self):
    try:
      self.conn = mdb.connect(Config.dbHost, Config.dbUser, Config.dbPwd, Config.dbDbName)
      self.cursor = self.conn.cursor(mdb.cursors.DictCursor)
      self.cursor.execute("CREATE TABLE IF NOT EXISTS \
              MacUpdates(id INT PRIMARY KEY AUTO_INCREMENT, \
                         version VARCHAR(64), \
                         dmg_path VARCHAR(255), \
                         dmg_size INTEGER, \
                         rel_notes TEXT, \
                         dsa_signature VARCHAR(100), \
                         pub_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
      self.cursor.execute("CREATE TABLE IF NOT EXISTS \
              UncensorDomains(id INT PRIMARY KEY AUTO_INCREMENT, \
                              srcDomain VARCHAR(255), \
                              dstDomain VARCHAR(255))")
      self.cursor.execute("CREATE TABLE IF NOT EXISTS \
              UncensorProxy(id INT PRIMARY KEY AUTO_INCREMENT, \
                            domain VARCHAR(255), \
                            iso CHAR(2))")
      self.cursor.execute("CREATE TABLE IF NOT EXISTS \
              UsageStats(id INT PRIMARY KEY AUTO_INCREMENT, \
                         stats_date DATE, \
                         version VARCHAR(64), \
                         mac_uncensor_requests INTEGER UNSIGNED, \
                         win_uncensor_requests INTEGER UNSIGNED, \
                         UNIQUE(stats_date), \
                         CONSTRAINT dateVersion UNIQUE (stats_date, version) \
                        )")

      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
        
  def cleanup(self):
    try:
      self.cursor.close()
      self.conn.close()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
  
  # Following methods are working with MacUpdates table
  # ===================================================
  def fetch_by_id(self, id_):
    try:
      self.cursor.execute("SELECT \
            id, version, dmg_path, dmg_size, rel_notes, dsa_signature, UNIX_TIMESTAMP(pub_date) AS pub_ts \
          FROM MacUpdates \
          WHERE id='%s'" % (mdb.escape_string(str(id_)), ))
      return self.cursor.fetchone()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return None
      
  
  def fetch_latest(self):
    try:
      self.cursor.execute("SELECT \
          id, version, dmg_path, dmg_size, rel_notes, dsa_signature, UNIX_TIMESTAMP(pub_date) AS pub_ts \
        FROM MacUpdates \
        ORDER BY pub_date DESC \
        LIMIT 1")
      return self.cursor.fetchone()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
    
    return None
    
  def fetch_several_latest(self, numRecords):
    try:
      self.cursor.execute("SELECT \
          id, version, dmg_path, dmg_size, rel_notes, dsa_signature, UNIX_TIMESTAMP(pub_date) AS pub_ts \
        FROM MacUpdates \
        ORDER BY pub_date DESC \
        LIMIT %d" % (numRecords))
      return self.cursor.fetchall()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
    
    return [];
        
  def insert(self, insertInfo):
    try:
      self.cursor.execute("INSERT INTO MacUpdates SET version='%s', dmg_path='%s', dmg_size='%s', rel_notes='%s', dsa_signature='%s'" %
        (mdb.escape_string(insertInfo['version']), 
         mdb.escape_string(insertInfo['dmg_path']),
         mdb.escape_string(insertInfo['dmg_size']),
         mdb.escape_string(insertInfo['rel_notes']),
         mdb.escape_string(insertInfo['dsa_signature'])
        ))
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
    
  def update(self, updateInfo):
    try:
      self.cursor.execute("UPDATE MacUpdates SET version='%s', dmg_path='%s', dmg_size='%s', rel_notes='%s', dsa_signature='%s' \
        WHERE id='%s'" %
        (mdb.escape_string(updateInfo['version']), 
         mdb.escape_string(updateInfo['dmg_path']),
         mdb.escape_string(updateInfo['dmg_size']),         
         mdb.escape_string(updateInfo['rel_notes']),
         mdb.escape_string(updateInfo['dsa_signature']),
         mdb.escape_string(str(updateInfo['id']))
        ))
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
      
  def delete(self, id_):
    try:
      self.cursor.execute("DELETE FROM MacUpdates WHERE id='%s'" %
        (mdb.escape_string(str(id_))) 
      )
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)        
      
  def uncensor_fetch_by_id(self, id_):
    try:
      self.cursor.execute("SELECT id, srcDomain, dstDomain  \
          FROM UncensorDomains \
          WHERE id='%s'" % (mdb.escape_string(str(id_)), ))
      return self.cursor.fetchone()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return None
    
  def uncensor_fetch_all(self):
    try:
      self.cursor.execute("SELECT id, srcDomain, dstDomain FROM UncensorDomains ORDER BY srcDomain ASC")
      return self.cursor.fetchall()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return []
    
  def uncensor_insert(self, insertInfo):
    try:
      self.cursor.execute("INSERT INTO UncensorDomains SET srcDomain='%s', dstDomain='%s'" %
        (mdb.escape_string(insertInfo['srcDomain']), 
         mdb.escape_string(insertInfo['dstDomain'])
        ))
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)
  
  def uncensor_delete(self, id_):
    try:
      self.cursor.execute("DELETE FROM UncensorDomains WHERE id='%s'" %
        (mdb.escape_string(str(id_))) 
      )
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

  def uncensorp_fetch_by_id(self, id_):
    try:
      self.cursor.execute("SELECT id, domain, iso  \
          FROM UncensorProxy \
          WHERE id='%s'" % (mdb.escape_string(str(id_)), ))
      return self.cursor.fetchone()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return None

  def uncensorp_fetch_all(self):
    try:
      self.cursor.execute("SELECT id, domain, iso FROM UncensorProxy ORDER BY iso ASC, domain ASC")
      return self.cursor.fetchall()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return []

  def uncensorp_fetch_by_iso(self, iso_code):
    try:
      self.cursor.execute("SELECT domain FROM UncensorProxy WHERE iso='%s' \
            ORDER BY domain ASC"
            % (mdb.escape_string(iso_code)))
      return self.cursor.fetchall()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

    return []

  def uncensorp_insert(self, insertInfo):
    try:
      self.cursor.execute("INSERT INTO UncensorProxy SET domain='%s', iso='%s'" %
        (mdb.escape_string(insertInfo['domain']),
         mdb.escape_string(insertInfo['iso'])
        ))
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

  def uncensorp_delete(self, id_):
    try:
      self.cursor.execute("DELETE FROM UncensorProxy WHERE id='%s'" %
        (mdb.escape_string(str(id_))) 
      )
      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

  def stats_add(self, version, os):
    try:
      if os == 'win':
        self.cursor.execute("INSERT INTO UsageStats (stats_date, version, \
            mac_uncensor_requests, win_uncensor_requests) VALUES \
            (DATE(NOW()), '%s', 0, 1) ON DUPLICATE KEY UPDATE \
              win_uncensor_requests=win_uncensor_requests+1" % version)
      elif os == 'mac':
        self.cursor.execute("INSERT INTO UsageStats (stats_date, version, \
            mac_uncensor_requests, win_uncensor_requests) VALUES \
            (DATE(NOW()), '%s', 1, 0) ON DUPLICATE KEY UPDATE \
              mac_uncensor_requests=mac_uncensor_requests+1" % version)

      self.conn.commit()
    except mdb.Error, e:
      log.msg("MySQL error %d: %s" % (e.args[0],e.args[1]))
      sys.exit(1)

