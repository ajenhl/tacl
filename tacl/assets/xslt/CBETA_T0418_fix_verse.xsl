<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Add tei:lg/tei:l around some verse text that occurs within a
       tei:app/tei:rdg within a prose context (that is, no ancestral
       tei:l). -->

  <xsl:template match="tei:app[@from='#beg0906007a']/tei:rdg">
    <xsl:call-template name="wrap-verse"/>
  </xsl:template>

  <xsl:template match="tei:app[@from='#beg0906007b']/tei:rdg">
    <xsl:call-template name="wrap-verse"/>
  </xsl:template>

  <xsl:template match="tei:app[@from='#beg0907018a']/tei:rdg">
    <xsl:call-template name="wrap-verse"/>
  </xsl:template>

  <xsl:template match="tei:app[@from='#beg0907018b']/tei:rdg">
    <xsl:call-template name="wrap-verse"/>
  </xsl:template>

  <xsl:template match="tei:app/@from"/>

  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template name="wrap-verse">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <tei:lg>
        <tei:l>
          <xsl:apply-templates select="node()"/>
        </tei:l>
      </tei:lg>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
